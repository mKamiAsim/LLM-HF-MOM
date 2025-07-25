from logging import Logger
from models import MomResponse
import core.app_configuration as config
from core import EventBus
import os
from huggingface_hub import login
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
import gc
import asyncio
from fastapi import Request

from services.shared_data_service import SharedDataService


class MomService:
    
    def __init__(self, logger:Logger, event_bus: EventBus ):
        self.logger = logger        
        self.event_bus = event_bus

    
    """
    Service for handling operations related to mother's responses.
    """
    def generate_mom(self, audio: bytes) -> MomResponse:                
        response= MomResponse(
            id=1,
            content="Sample MOM response generated from audio",
            timestamp="2023-10-01T12:00:00Z",
            length =len(audio)
        )
        # self.logger.info("Generated MOM response {@Response}", Response = response.dict())
        self.logger.info("Generated MOM response", Response = response.dict())      
        return response
    
    async def download_quantized_model_from_huggingface(self, model_name: str = config.LLAMA) -> bool:
        """
        Downloads a quantized model from Hugging Face.
        """
        status = False
        model_path = os.path.join(config.LLM_MODEL_PATH, model_name)        
        if os.path.exists(model_path):
            self.logger.info(f"Model {model_name} already exists at {model_path}.")
            status = True
            self.event_bus.publish("model_status",{"Status": status, "Message": "Model already exists and does not need to be downloaded. Model is ready to use."})
            return status
        
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            self.event_bus.publish("model_status",{"Status": status, "Message": "HF_TOKEN environment variable is not set. Please set it to download the model."})        
            raise ValueError("HF_TOKEN environment variable is not set.")
        
        login(token=hf_token, add_to_git_credential=True)
                    
                        
        self.logger.info(f"Downloading quantized model: {model_name}")
        
        quant_config = config.QUANT_CONFIG
        self.event_bus.publish("model_status",{"Status": status, "Message": "Downloading model... Please wait."})        
        def load_model():
            return AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", quantization_config=quant_config)
        def load_tokenizer():
            return AutoTokenizer.from_pretrained(model_name)    
            
        model, tokenizer = await asyncio.to_thread(load_model), await asyncio.to_thread(load_tokenizer)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        status = True
        self.logger.info(f"Model {model_name} downloaded and saved to {model_path}.")
        self.event_bus.publish("model_status",{"Status": status, "Message": "Model downloaded and saved successfully. Model is ready to use."}) 
        
        return status


