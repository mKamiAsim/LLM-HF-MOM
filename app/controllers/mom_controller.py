from fastapi import APIRouter, Depends, Request, UploadFile, File, BackgroundTasks
from core.di import IMOMService
from services import MomService
from models import MomResponse
from typing import Dict


router = APIRouter(prefix="/mom", tags=["Minutes of Meeting (MOM)"])

@router.post("/generate", response_model=MomResponse, summary="Generate a sample MOM response")
async def generate_mom( background_tasks:BackgroundTasks, audio: UploadFile = File(...),  mom_service: MomService = Depends(IMOMService)):
    content = await audio.read()
    return await mom_service.generate_mom(audio=content, file_name=audio.filename, background_tasks=background_tasks)

@router.get("/getModelStatus", response_model=Dict,  summary="Get the status of the model download")
def getModelStatus(request:Request):
    request.app.state.shared_data.get_model_download_status()