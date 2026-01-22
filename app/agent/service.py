import os 
import json
import re
from fastapi import UploadFile, File, HTTPException
import app.agent.utils as utils
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Create a simple string-output agent since llama3.1 adds markdown formatting
model = OpenAIModel('llama3.1', provider=OpenAIProvider(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ))
simple_agent = Agent(model, output_type=str)

async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or TXT file."
        )
    
    file_location = f"./uploads/{file.filename}"
    try:
        os.makedirs("./uploads", exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        utils.process_file(file_location)

        return {"message": f"File '{file.filename}' uploaded and indexed successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(file_location):
           os.remove(file_location)

def extract_json_from_text(text: str) -> dict:
    """Extract JSON from LLM response that has markdown code blocks."""
    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = text.replace('```', '')
    
    # Remove common prefixes
    text = re.sub(r'^(?:Here is the JSON:|Here\'s the JSON:|JSON:)\s*\n*', '', text, flags=re.IGNORECASE)
    
    # Try to find JSON object
    json_match = re.search(r'\{[^{}]*"availability"[^{}]*"next_slot"[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(0)
            # Clean up any extra whitespace or newlines inside the JSON
            json_str = re.sub(r'\s+', ' ', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"Attempted to parse: {json_str}")
    
    # Try direct parse after cleaning
    try:
        cleaned = text.strip()
        return json.loads(cleaned)
    except:
        pass
    
    # Manual extraction as last resort
    avail_match = re.search(r'"availability"\s*:\s*"(Available|Busy)"', text)
    slot_match = re.search(r'"next_slot"\s*:\s*"([^"]*)"', text)
    
    if avail_match and slot_match:
        return {
            "availability": avail_match.group(1),
            "next_slot": slot_match.group(1)
        }
    
    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")

async def ask_question(query: str):
    context = utils.find_relevant_context(query, top_k=5)

    if not context:
        raise HTTPException(status_code=404, detail="No schedule data found.")
    
    prompt = f"""You are analyzing a weekly schedule to answer availability questions.

SCHEDULE:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Convert the time in the question to 24-hour format (3pm = 15:00, 3am = 03:00)
2. Check if any schedule entry is happening at that exact time
3. An entry like "Wednesday 16:00-18:00" means busy from 16:00 to 18:00
4. Determine availability:
   - If the requested time falls within any entry's time range: "Busy"
   - Otherwise: "Available"
5. For next_slot:
   - If BUSY: show when the current event ends and what time they become available
   - If AVAILABLE: show the next upcoming event

Respond with ONLY this JSON (no explanation, no markdown):
{{"availability": "Available or Busy", "next_slot": "when available or next event"}}

Examples:
- If asking about Monday 3pm (15:00) and "Monday 14:00-15:30 Client Call" is happening:
  {{"availability": "Busy", "next_slot": "Available after 15:30"}}
  
- If asking about Wednesday 3pm (15:00) between "13:00-14:00 Team Sync" and "16:00-18:00 Deep Focus Work":
  {{"availability": "Available", "next_slot": "Next event: Deep Focus Work at 16:00"}}"""

    try:
        result = await simple_agent.run(prompt)
        raw_response = result.output
        
        print(f"\n{'='*60}")
        print(f"📥 Raw LLM response:")
        print(f"{'='*60}")
        print(raw_response)
        print(f"{'='*60}\n")
        
        # Parse the response
        parsed = extract_json_from_text(raw_response)
        
        print(f"✅ Successfully parsed: {parsed}\n")
        
        return {
            "availability": parsed["availability"],
            "next_available_time_slot": parsed["next_slot"]
        }
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")