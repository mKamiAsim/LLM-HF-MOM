from fastapi import Request
from services import MomService, SharedDataService
from core.log_provider import get_logger
from core import EventBus

event_bus = EventBus()

def IMOMService():
    return MomService(logger=get_logger("MomService"), event_bus=event_bus) 

def ISharedDataService():    
    return SharedDataService(event_bus=event_bus)

def IEventBus():
    return event_bus
