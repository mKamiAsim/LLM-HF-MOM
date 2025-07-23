from fastapi import Request
from services import MomService, SharedDataService
from core.log_provider import get_logger


def IMOMService(request: Request):
    return MomService(logger=get_logger(), shared_data_service=ISharedDataService(), request=request) 

def ISharedDataService():    
    return SharedDataService()
