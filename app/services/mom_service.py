from logging import Logger
import tempfile

from models import MomResponse
import core.app_configuration as config
from core import EventBus
import os
import io
from huggingface_hub import login
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, TextStreamer, pipeline
import torch
import gc
import asyncio
from fastapi import BackgroundTasks, Depends
import openai
from datetime import datetime
import soundfile as sf
import numpy as np

from services.shared_data_service import SharedDataService


class MomService:
    
    def __init__(self, logger:Logger, event_bus: EventBus ):
        self.logger = logger        
        self.event_bus = event_bus
        self.model = None
        self.tokenizer = None
        self.model_name= config.LLAMA_1B        
        self._load_model()
        
    
    def _load_model(self):
        try:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.asr= pipeline("automatic-speech-recognition",model=config.AUDIO_MODEL, device="cuda")
            self.model_loading= False
        except Exception as e:
            self.logger.error(f"Error loading model {self.model_name}: {str(e)}")
            self.model_loading= True
        

    
    """
    Service for handling operations related to mother's responses.
    """
    async def generate_mom(self, audio: bytes, file_name: str, background_tasks:BackgroundTasks) -> MomResponse:
        
        if(self.model_loading):
            return MomResponse(
                status=503,
                mom_content="System is warming up, please try again later.",
                timestamp=datetime.now(),  # Placeholder for actual timestamp
                audio_text=""
            )
        
       
        self.logger.info("Generating MOM response from audio file: %s", file_name)             
        audio_text = ""
        try:            
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
        
        system_message = "You are an assistant that produces minutes of meetings from transcripts, with summary, key discussion points, takeaways and action items with owners, in markdown. Do not add transcript in the minutes."
        user_prompt = f"Below is an extract transcript. Please write minutes in markdown, including a summary with attendees, location and date; discussion points; takeaways; and action items with owners.\n{audio_text}"
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        device = "cuda" if torch.cuda.is_available() else "cpu" 
        self.logger.info(f"Using device: {device}")           
        self.model.to(device)    
        inputs = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to(device)
        streamer = TextStreamer(self.tokenizer)
        output= self.model.generate( inputs, max_new_tokens=2000, streamer=streamer, do_sample=True, temperature=0.7)
        
        # response_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        generated_tokens = output[0][inputs.shape[-1]:]
        response_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
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
        audio_buffer = io.BytesIO(audio)
        audio_array, samplerate = sf.read(audio_buffer)
        if len(audio_array.shape) > 1:
            # Average across channels if multi-channel
            audio_array = np.mean(audio_array, axis=1).astype(audio_array.dtype)
            
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)
        
        def chunk_audio(data, samplerate, chunk_length_s):
            chunk_samples = chunk_length_s * samplerate
            for start in range(0, len(data), chunk_samples):
                yield data[start:start + chunk_samples]
        
        texts = []
        for chunk in chunk_audio(audio_array, samplerate, 30):
            result = self.asr({"array": chunk, "sampling_rate": samplerate})
            texts.append(result["text"].strip())
        
        return " ".join(texts)
           
    
    
    
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
    
    


