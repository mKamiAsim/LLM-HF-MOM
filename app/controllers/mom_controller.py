from fastapi import APIRouter, Depends, Request
from core.di import IMOMService
from services import MomService
from models import MomResponse


router = APIRouter(prefix="/mom", tags=["Minutes of Meeting (MOM)"])

@router.get("/generate", response_model=MomResponse, summary="Generate a sample MOM response")
def generate_mom(mom_service: MomService = Depends(IMOMService)):
    return mom_service.generate_mom()

@router.get("/getModelStatus", response_model=str,  summary="Get the status of the model download")
def getModelStatus(request:Request):
    return request.app.state.shared_data.get_model_download_status()