
from dotenv import dotenv_values
from llama import Llama, Dialog  # type: ignore


SYSPROMPT_VERSION = "2023-10-19"
LLAMA_VARIANT = "13b-chat"
LLAMA_TEMP = 0.6

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']


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
	


	generator = Llama.build(
		ckpt_dir=f".venv/src/llama/llama-2-{LLAMA_VARIANT}",
		tokenizer_path=".venv/src/llama/tokenizer.model",
		max_seq_len=4096,
		max_batch_size=10
	)

	results = generator.chat_completion(
		messages=get_messages([s['description'] for s in selections]),
		temperature=LLAMA_TEMP,
		max_gen_len=None
	)
