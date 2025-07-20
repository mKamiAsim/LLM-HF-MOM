from services import MomService
from core.logging_config import logger

def IMOMService():
    return MomService(logger=logger)
