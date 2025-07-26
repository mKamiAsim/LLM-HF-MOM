from pydantic import BaseModel, Field
from datetime import datetime

class MomResponse(BaseModel):
    """
    Model representing a response from a mother.
    """
    status: int = Field( description="Status code of the response")
    mom_content: str = Field( description="Content of the MOM response")
    timestamp:datetime = Field( description="Timestamp of when the response was created")
    audio_text: str = Field(description="Transcribed text from the audio file", default="")
    
