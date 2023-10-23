
import re
from dotenv import dotenv_values
from ruamel.yaml import YAML
from llama_cpp import Llama
# from generator.models.llama2 import llm

SYSPROMPT_VERSION = "2023-10-19"
LLAMA_VARIANT = "13b-chat"
LLAMA_TEMP = 1.8

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

config = dotenv_values()
LLAMA_MODEL_PATH = f"{config['LLAMA_MODELS_DIR']}/llama-2-{LLAMA_VARIANT}/quant-Q8_0.gguf"

with open(f'systemprompts/descriptions/systemprompt_llama2_{SYSPROMPT_VERSION}.txt', 'rt') as f:
	systemprompt = f.read()

def get_messages(n):
	return [
		{
			"role": "system",
			"content": systemprompt
		},
		{
			"role": "user",
			"content": f"Please generate {n} descriptions of pieces of hypothetical music. Remember to use YAML format for your response."
		}
	]

def get_descriptions_llama2(n):
	llm = Llama(
		model_path=LLAMA_MODEL_PATH,
		n_gpu_layers=-1,
		n_ctx=2048,
		seed=-1
	  )
	messages = get_messages(n)
	print(messages)
	for i in range(20):
		try:
			results = llm.create_chat_completion(
				messages=messages,
				temperature=LLAMA_TEMP,
				max_tokens=2000
			)

			raw_descs = results['choices'][0]['message']['content']
			print(raw_descs)

			m = re.search(r'(- ".+?"\n?)+', raw_descs)
			# error handling goes here
			if m:
				yaml_list = m.group()
				# ..and here
				return yaml.load(yaml_list)
			break
		except (ValueError, KeyError) as e:
			if i < 20:
				print(f"Error: {e.msg}. Retrying...")
			else:
				raise e("no regex match found in llama2 descriptions output")


# def test_run(n, runs):
# 	all_results = []
# 	for _ in range(runs):
# 		r = llm.create_chat_completion(
# 			messages=get_messages(n),
# 			temperature=LLAMA_TEMP,
# 			max_tokens=2000
# 		)
# 		all_results.append(r['choices'][0]['message']['content'])
# 	return all_results
