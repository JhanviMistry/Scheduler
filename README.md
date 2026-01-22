# Local RAG Schedule Assistant

A **local Retrieval-Augmented Generation (RAG) AI agent** that understands your weekly schedule and answers availability questions like:

> *"Am I free on Wednesday from 3–5 PM?"*

Everything runs **locally** — no cloud dependency — using embeddings, SQLite, and a schema‑validated AI agent.

---

## 🚀 Features

* 📄 Upload a `schedule.txt` or PDF file
* 🔎 Semantic search over your schedule using embeddings
* 🧠 AI agent answers availability questions
* 📦 Local SQLite vector database
* 🔐 Strict schema validation with **pydantic-ai**
* ⚡ FastAPI backend
* 🏠 Fully local (Ollama-compatible models)

---

## 🧱 Architecture Overview

```
User Query
   ↓
Semantic Retrieval (SQLite + embeddings)
   ↓
Relevant Schedule Context
   ↓
AI Agent (pydantic-ai)
   ↓
Structured JSON Response
```

---

## 📁 Project Structure

```
app/
├── agent/
│   ├── controller.py      # API routes
│   ├── model.py           # Pydantic output schema
│   ├── utils.py           # Vector DB, embeddings, retrieval
│   └── service.py         # File upload & query logic
│
├── ai_model.py         # AI agent + model config
├── main.py             # FastAPI entry point
├── templates/
│   ├── index.html      
│
├── uploads/            # Temporary uploads
└── knowledge_base.db   # Local SQLite vector store


---

## 📝 Schedule Format (Important)

Your schedule **must follow this format** for accurate results:

```
Wednesday 16:00-18:00 Deep Focus Work
Friday 19:00-21:00 Movie Night
```

Rules:

* One event per line
* Day name spelled fully
* 24‑hour time format (`HH:MM-HH:MM`)

---

## 🧪 Example Questions

* `Am I free on Wednesday from 15:00 to 16:00?`
* `Do I have anything Friday evening?`
* `What is my next scheduled task?`

---

## ⚙️ Tech Stack

* **FastAPI** – API framework
* **pydantic-ai** – Schema‑validated AI agent
* **Sentence Transformers** – Local embeddings
* **SQLite** – Vector database
* **Ollama** – Local LLM runtime

---

## ▶️ Running the Project

### 1️⃣ Start Ollama

Make sure Ollama is running:

```bash
ollama serve
```

Pull the model:

```bash
ollama pull llama3.1
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Run the API

```bash
uvicorn app.main:app --reload
```

---

### 4️⃣ Upload Schedule

Use `/upload` endpoint to upload `schedule.txt`.

---

### 5️⃣ Ask Questions

Send a POST request to `/ask` with your query.

---

## 🧠 Why RAG for Scheduling?

Schedules are **semi‑structured**:

* Too rigid for pure rule‑based systems
* Too precise for pure LLM guessing

RAG lets us:

* Retrieve relevant time blocks
* Let the AI reason *only* over what matters
* Enforce correctness with schemas

---

## 🔐 Output Schema

The AI always responds in this format:

```json
{
  "availability": "Available" | "Busy",
  "next_slot": "string"
}
```

This guarantees predictable, machine‑readable output.

---

## 🛠️ Future Improvements

* ⏱ Deterministic time overlap checking
* 📅 Calendar view / UI
* 🧠 Natural language time parsing ("after lunch")
* 📊 Free‑slot recommendations

---

## 👤 Author

Built as a **local-first AI agent experiment** to explore RAG, schema enforcement, and agent reliability.

---

✨ *If it runs locally, it runs forever.*
