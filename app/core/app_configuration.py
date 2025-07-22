from transformers import BitsAndBytesConfig
import torch

LLM_MODEL_PATH = "assets/models"
LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"

QUANT_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)