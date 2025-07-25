from fastapi import APIRouter, Depends, Request, UploadFile, File
from core.di import IMOMService
from services import MomService
from models import MomResponse
from typing import Dict


router = APIRouter(prefix="/mom", tags=["Minutes of Meeting (MOM)"])

@router.post("/generate", response_model=MomResponse, summary="Generate a sample MOM response")
async def generate_mom( audio: UploadFile = File(...), mom_service: MomService = Depends(IMOMService)):
    content = await audio.read()
    return mom_service.generate_mom(content)

@router.get("/getModelStatus", response_model=Dict,  summary="Get the status of the model download")
def getModelStatus(request:Request):
    return request.app.state.shared_data.get_model_download_status()