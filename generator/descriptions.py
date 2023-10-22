
from json import loads, JSONDecodeError
from dotenv import dotenv_values
from halo import Halo
import openai
from openai import ChatCompletion
from openai.error import APIError

SYSPROMPT_VERSION = '2023-10-15'
MODEL = 'gpt-4'

config = dotenv_values()


def get_descriptions(n):
	match MODEL:
		case 'gpt-4':
			return get_descriptions_gpt4(n)
		case 'llama2':
			raise NotImplementedError()
		case _:
			raise ValueError("Descriptions MODEL is not correctly specified")



openai.organization = config['OPENAI_ORG']
openai.api_key = config['OPENAI_KEY']


generate_music_function = {
	"name": "generate_music",
	"description": "generate a snippet of music according to a description",
	"parameters": {
		"type": "object",
		"properties": {
			"prompt": {
				"type": "array",
				"description": "descriptions of the music to be generated",
				"items": {
					"type": "string"
				}
			}
		},
		"required": ["prompt"]
	}
}

with open(f'systemprompts/descriptions/systemprompt_gpt-4_{SYSPROMPT_VERSION}.txt', 'rt') as f:
	systemprompt = f.read()

def get_messages(n):
	return [
		{
			"role": "system",
			"content": systemprompt
		},
		{
			"role": "user",
			"content": f"Please generate {n} descriptions of music selections."
		}
	]

def get_descriptions_gpt4(n):
	# print(f"generating {n} descriptions...  ")
	with Halo(f"generating {n} descriptions"):
		for i in range(3):
			try:
				results = ChatCompletion.create(
					model="gpt-4",
					messages=get_messages(n),
					function_call={"name": "generate_music"},
					functions=[generate_music_function]
				)
				arguments = results['choices'][0]['message']['function_call']['arguments']
				descriptions = loads(arguments)['prompt']
				break
			except (APIError, JSONDecodeError) as e:
				if i < 2:
					print(f"Error: {e.msg}. Retrying...")
				else:
					raise APIError("Max retries reached")
	print(f"generated {len(descriptions)} descriptions")
	return descriptions

