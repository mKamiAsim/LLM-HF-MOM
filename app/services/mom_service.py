from logging import Logger

from models import MomResponse
import core.app_configuration as config
from core import EventBus
import os
import io
from huggingface_hub import login
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
import gc
import asyncio
from fastapi import BackgroundTasks, Depends
import openai
from datetime import datetime

from services.shared_data_service import SharedDataService


class MomService:
    
    def __init__(self, logger:Logger, event_bus: EventBus ):
        self.logger = logger        
        self.event_bus = event_bus

    
    """
    Service for handling operations related to mother's responses.
    """
    async def generate_mom(self, audio: bytes, file_name: str, background_tasks:BackgroundTasks, model_name: str = config.LLAMA) -> MomResponse:
        
        model_path = os.path.join(config.LLM_MODEL_PATH, model_name)        
        if not os.path.exists(model_path):
            self.logger.info(f"Model {model_name} not available in {model_path}. Requested to download the model.")
            background_tasks.add_task(self.download_quantized_model_from_huggingface, model_name)
            return MomResponse(
                status=404,
                mom_content="Model not available. Please wait while the model is being downloaded.",
                timestamp=datetime.now(),  # Placeholder for actual timestamp
                audio_text=""
            )
                     
        audio_text = ""
        try:
            self.logger.info("Generating MOM response from audio file: %s", file_name)
            audio_text = await self.convert_audio_to_text(audio, file_name)
            
        except Exception as e:
            self.logger.error("Error converting audio to text: %s", str(e))
            return MomResponse( 
                status=500,
                mom_content="Error processing audio file",
                timestamp=datetime.now(),
                audio_text=""
            )
        
        if not audio_text:
            self.logger.error("No text extracted from audio file.")
            return MomResponse(
                status=400,
                mom_content="No text extracted from audio file",
                timestamp=datetime.now(),
                audio_text=""
            )
        
        system_message = "You are an assistant that produces minutes of meetings from transcripts, with summary, key discussion points, takeaways and action items with owners, in markdown."
        user_prompt = f"Below is an extract transcript. Please write minutes in markdown, including a summary with attendees, location and date; discussion points; takeaways; and action items with owners.\n{audio_text}"
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
                
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        streamer = TextStreamer(tokenizer)
        output= model.generate( inputs, max_new_tokens=2000, streamer=streamer, do_sample=True, temperature=0.7)
        response_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        self.logger.info("MOM response generated successfully.")
        return MomResponse(
            status=200,
            mom_content=response_text,
            timestamp=datetime.now(),  # Placeholder for actual timestamp
            audio_text=audio_text
        )     
              
        
    async def convert_audio_to_text(self, audio: bytes, file_name = str) -> str:
        """
        Converts audio to text using Whisper model.
        """
        audio_file = io.BytesIO(audio)
        audio_file.name = file_name
        
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:            
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        transcription = openai.audio.transcriptions.create(model=config.AUDIO_MODEL, file=audio_file, response_format="text")        
        return transcription
    
    
    async def download_quantized_model_from_huggingface(self, model_name: str) -> bool:
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
            tokenizer= AutoTokenizer.from_pretrained(model_name)    
            tokenizer.pad_token = tokenizer.eos_token
            return tokenizer
            
        model, tokenizer = await asyncio.to_thread(load_model), await asyncio.to_thread(load_tokenizer)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        status = True
        self.logger.info(f"Model {model_name} downloaded and saved to {model_path}.")
        self.event_bus.publish("model_status",{"Status": status, "Message": "Model downloaded and saved successfully. Model is ready to use."}) 
        
        return status
    
    


