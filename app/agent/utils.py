import fitz  # PyMuPDF 
import sqlite3
import numpy as np
from typing import Optional, List
from sentence_transformers import SentenceTransformer 
import re

# Initialize the embedding model locally
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_db_connection():
    conn = sqlite3.connect('knowledge_base.db')
    conn.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, text TEXT, embedding BLOB)')
    return conn

def embed_text(text: str):
    """Converts text into a vector (embedding) using sentence-transformers."""
    embedding = model.encode(text, convert_to_numpy=True).astype('float32')
    return embedding.tolist()

def insert_document(text: str, embedding: list):
    """Saves the document text and its embedded blob to the database."""
    conn = get_db_connection()
    embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
    conn.execute('INSERT INTO documents (text, embedding) VALUES (?, ?)', (text, embedding_blob))
    conn.commit()
    conn.close()

def fetch_all_documents():
    conn = get_db_connection()
    cursor = conn.execute('SELECT id, text, embedding FROM documents')
    rows = cursor.fetchall()
    conn.close()
    
    docs = []
    for doc_id, text, emb_blob in rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        if emb.shape[0] == 384:
            docs.append((doc_id, text, emb))
        else:
            print(f"⚠️ Skipping incompatible {emb.shape[0]}-dim vector (expected 384)")
    return docs

def cosine_similarity(v1, v2):
    """Calculates semantic matching between two vectors."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def process_file(file_path: str):
    """Logic to 'chop up' files and save them as vectors."""
    text = ""
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        text = "".join([page.get_text() for page in doc])
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    chunks = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            chunks.append(line)
    
    print(f"📄 Processing {len(chunks)} chunks from {file_path}")
    for chunk in chunks:
        embedding = embed_text(chunk)
        insert_document(chunk, embedding)
    print(f"✅ Indexed {len(chunks)} schedule entries")

def extract_day_from_query(query: str) -> Optional[str]:
    """Extract day of week from user query."""
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    query_lower = query.lower()
    for day in days:
        if day in query_lower:
            return day.capitalize()
    return None

def find_relevant_context(query: str, top_k: int = 3) -> Optional[str]:
    """Enhanced semantic search with day-based filtering."""
    # First, try to extract the day from the query
    target_day = extract_day_from_query(query)
    
    query_embedding = embed_text(query)
    docs = fetch_all_documents()

    if not docs:
        print("⚠️ No documents found in database")
        return None

    # If we detected a specific day, prioritize entries from that day
    if target_day:
        print(f"🎯 Filtering for {target_day} entries")
        day_docs = [(doc_id, text, emb) for doc_id, text, emb in docs if target_day in text]
        
        if day_docs:
            # Calculate similarities only for that day's entries
            similarities = [
                (doc_id, text, cosine_similarity(query_embedding, emb))
                for doc_id, text, emb in day_docs
            ]
            similarities.sort(key=lambda x: x[2], reverse=True)
            top_docs = similarities[:top_k]
            
            print(f"🔍 Top {len(top_docs)} {target_day} matches:")
            for idx, (doc_id, text, score) in enumerate(top_docs, 1):
                print(f"  {idx}. [{score:.3f}] {text}")
            
            return "\n".join([doc[1] for doc in top_docs])
    
    # Fallback to regular semantic search
    similarities = [
        (doc_id, text, cosine_similarity(query_embedding, emb))
        for doc_id, text, emb in docs
    ]
    similarities.sort(key=lambda x: x[2], reverse=True)
    top_docs = similarities[:top_k]

    print(f"🔍 Top {top_k} matches for query: '{query}'")
    for idx, (doc_id, text, score) in enumerate(top_docs, 1):
        print(f"  {idx}. [{score:.3f}] {text[:80]}")

    return "\n".join([doc[1] for doc in top_docs])