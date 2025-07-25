from pydantic import BaseModel, Field

class MomResponse(BaseModel):
    """
    Model representing a response from a mother.
    """
    id: int = Field(..., description="Unique identifier for the response")
    content: str = Field(..., description="Content of the mother's response")
    timestamp: str = Field(..., description="Timestamp of when the response was created")
    length: int = Field(description="Length of the audio content in bytes")
    
