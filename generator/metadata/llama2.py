
import re
from dotenv import dotenv_values
from ruamel.yaml import YAML
from llama_cpp import Llama
# from ..models.llama2 import llm

SYSPROMPT_VERSION = "2023-10-19"
LLAMA_VARIANT = "13b-chat"
LLAMA_TEMP = 1.8
LLAMA_MAX_TOKENS = 3000

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

config = dotenv_values()
LLAMA_MODEL_PATH = f"{config['LLAMA_MODELS_DIR']}/llama-2-{LLAMA_VARIANT}/quant-Q8_0.gguf"

with open(f'systemprompts/metadata/systemprompt_llama2_{SYSPROMPT_VERSION}.txt', 'rt') as f:
	systemprompt = f.read()

def get_messages(descriptions):
	descs_str = '\n'.join(map(lambda p: f"- {p}", descriptions))
	return [
		{
			"role": "system",
			"content": systemprompt
		},
		{
			"role": "user",
			"content": f"Please generate {len(descriptions)} sets of artist/title/year metadata for the given descriptions: \n{descs_str}"
		}
	]

def get_metadata_llama2(selections):
	llm = Llama(
		model_path=LLAMA_MODEL_PATH,
		n_gpu_layers=-1,
		n_ctx=2048,
		seed=-1
	  )

	for i in range(20):
		try:
			results = llm.create_chat_completion(
				messages=get_messages([s['description'] for s in selections]),
				temperature=LLAMA_TEMP,
				max_tokens=LLAMA_MAX_TOKENS
			)
	
			raw_descs = results['choices'][0]['message']['content']
			print(raw_descs)

			m = re.finditer(r'(-\s+(?:artist:|title:|year:).+?)(?=\n\n|\Z)', raw_descs, re.S)
			# error handling goes here
			groups = [yaml.load(x.group()) for x in m]
			break
		except (ValueError, KeyError) as e:
			if i < 20:
				print(f"Error: {e.msg}. Retrying...")
			else:
				raise e("Max retries reached")


	for s, m in zip(selections, groups):
		# the [0] is a hack for now
		s['metadata'] = m[0]


def test_samples(s_id):
	with open(f"descriptions/samples/descs{s_id}.yaml", 'rt') as f:
		samples = yaml.load(f)
	get_metadata_llama2(samples)
	return samples