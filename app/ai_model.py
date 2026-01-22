# ai_model.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.agent.model import VirtualAssistantAgent

model = OpenAIModel(
    model_name="llama3.1",
    provider=OpenAIProvider(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
)

agent = Agent(
    model=model,
    output_type=VirtualAssistantAgent,
    retries=5,
    debug=True,
    system_prompt=(
        "You are a scheduling assistant.\n"
        "You MUST respond with a SINGLE valid JSON object.\n\n"
        "The response schema is EXACTLY:\n"
        "{\n"
        '  "availability": "Available" | "Busy",\n'
        '  "next_slot": string\n'
        "}\n\n"
        "Rules:\n"
        "- Do NOT include explanations\n"
        "- Do NOT include markdown\n"
        "- Do NOT include extra fields\n"
        "- Use ONLY the allowed values\n"
    )
)
