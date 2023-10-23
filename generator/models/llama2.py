
from dotenv import dotenv_values
from llama_cpp import Llama

LLAMA_VARIANT = '13b-chat'

config = dotenv_values()
LLAMA_MODEL_PATH = f"{config['LLAMA_MODELS_DIR']}/llama-2-{LLAMA_VARIANT}/quant-Q8_0.gguf"

llm = Llama(
		model_path=LLAMA_MODEL_PATH,
		n_gpu_layers=-1,
		n_ctx=2048,
		seed=-1
	  )