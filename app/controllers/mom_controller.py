from fastapi import APIRouter, Depends
from core.di import IMOMService
from services import MomService
from models import MomResponse


router = APIRouter(prefix="/mom", tags=["Minutes of Meeting (MOM)"])

@router.get("/generate", response_model=MomResponse, summary="Generate a sample MOM response")
def generate_mom(mom_service: MomService = Depends(IMOMService)):
    return mom_service.generate_mom()