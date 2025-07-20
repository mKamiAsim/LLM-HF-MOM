from logging import Logger
from models import MomResponse

class MomService:
    
    def __init__(self, logger:Logger):
        self.logger = logger
    
    """
    Service for handling operations related to mother's responses.
    """
    def generate_mom(self):                
        response= MomResponse(
            id=1,
            content="This is a sample response from the mother.",
            timestamp="2023-10-01T12:00:00Z"
        )
        # self.logger.info("Generated MOM response {@Response}", Response = response.dict())
        self.logger.info("Generated MOM response", Response = response.dict())
        return response

