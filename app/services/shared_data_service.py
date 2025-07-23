class SharedDataService:
    
    def __init__(self):
        self.model_download_status = ""

    
    def set_model_download_status(self, status: str):
       self.model_download_status = status
    
    def get_model_download_status(self) -> str:
        return self.model_download_status