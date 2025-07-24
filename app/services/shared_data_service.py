from core import EventBus
from typing import Dict
class SharedDataService:
    
    def __init__(self, event_bus: EventBus):
        self.model_download_status = {}
        event_bus.subscribe("model_status", self.set_model_download_status)

    
    def set_model_download_status(self, status: Dict):
       self.model_download_status = status
    
    def get_model_download_status(self) -> Dict:
        return self.model_download_status