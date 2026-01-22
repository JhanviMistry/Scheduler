from pydantic import BaseModel, Field

class VirtualAssistantAgent(BaseModel):
    # Use very simple names and clear, short descriptions
    availability: str 
    next_slot: str = Field(description="The very next time or task on the schedule.")