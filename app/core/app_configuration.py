from transformers import BitsAndBytesConfig
import torch

LLM_MODEL_PATH = "assets/models"
LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"
LLAMA_1B="meta-llama/Llama-3.2-1B-Instruct"
AUDIO_MODEL = "whisper-1"

QUANT_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)
