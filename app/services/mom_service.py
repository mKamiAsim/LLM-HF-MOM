from logging import Logger
from models import MomResponse
import core.app_configuration as config
import os
from huggingface_hub import login
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
import gc
import asyncio
from fastapi import Request

from services.shared_data_service import SharedDataService


class MomService:
    
    def __init__(self, logger:Logger, shared_data_service:SharedDataService, request:Request ):
        self.logger = logger
        self.shared_data_service = shared_data_service
        self.request = request
    
    """
    Service for handling operations related to mother's responses.
    """
    def generate_mom(self):                
        response= MomResponse(
            id=1,
            content="This is a sample response from the mother.",
            timestamp="2023-10-01T12:00:00Z"
        )
        # self.logger.info("Generated MOM response {@Response}", Response = response.dict())
        self.logger.info("Generated MOM response", Response = response.dict())      
        return response
    
    async def download_quantized_model_from_huggingface(self, model_name: str = config.LLAMA) -> bool:
        """
        Downloads a quantized model from Hugging Face.
        """
        model_path = os.path.join(config.LLM_MODEL_PATH, model_name)        
        if os.path.exists(model_path):
            self.logger.info(f"Model {model_name} already exists at {model_path}.")
            self.shared_data_service.set_model_download_status("Model already exists and does not need to be downloaded. Model is ready to use.")
            return True
        
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            self.shared_data_service.set_model_download_status("HF_TOKEN environment variable is not set. Please set it to download the model.")            
            raise ValueError("HF_TOKEN environment variable is not set.")
        
        login(token=hf_token, add_to_git_credential=True)
                    
                        
        self.logger.info(f"Downloading quantized model: {model_name}")
        
        quant_config = config.QUANT_CONFIG
        
        self.shared_data_service.set_model_download_status("Downloading model... Please wait.")
        def load_model():
            return AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", quantization_config=quant_config)
        def load_tokenizer():
            return AutoTokenizer.from_pretrained(model_name)    
            
        model, tokenizer = await asyncio.to_thread(load_model), await asyncio.to_thread(load_tokenizer)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        self.logger.info(f"Model {model_name} downloaded and saved to {model_path}.")
        self.shared_data_service.set_model_download_status("Model downloaded and saved successfully. Model is ready to use.")
        
        return True


