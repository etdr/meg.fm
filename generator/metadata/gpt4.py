
from json import loads, JSONDecodeError
from dotenv import dotenv_values
import openai
from openai import ChatCompletion, APIError

OPENAI_MODEL = "gpt-4-1106-preview"
SYSPROMPT_VERSION = "2023-10-15"

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']
openai.organization = config['OPENAI_ORG']
openai.api_key = config['OPENAI_KEY']

generate_metadata_function = {
	"name": "write_metadata",
	"description": "write a hypothetical title, artist, and year for a selection of music given a description of it to a file",
	"parameters": {
		"type": "object",
		"properties": {
			"metadata": {
				"type": "array",
				"description": "a list of artist/title/year metadata for the given descriptions",
				"items": {
					"type": "object",
					"properties": {
						"artist": {
							"type": "string",
							"description": "the name of the person or group who created the music"
						},
						"title": {
							"type": "string",
							"description": "the title of the track from which the selection was taken"
						},
						"year": {
							"type": "string",
							"description": "the year this piece of music was released"
						}
					}
				}
			}
		},
		"required": ["metadata"]
	}
}

with open(f'systemprompts/metadata/systemprompt_gpt-4_{SYSPROMPT_VERSION}.txt', 'rt') as f:
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

def get_metadata_gpt4(selections):
	for i in range(3):
		try:
			results = ChatCompletion.create(
				model=OPENAI_MODEL,
				messages=get_messages([s['description'] for s in selections]),
				function_call={"name": "write_metadata"},
				functions=[generate_metadata_function]
			)
			arguments = results['choices'][0]['message']['function_call']['arguments']
				# .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
			metadata = loads(arguments)['metadata']
		except (APIError, JSONDecodeError, KeyError) as e:
			if i < 2:
					print(f"Error: {e.msg}. Retrying...")
			else:
				raise e("Max retries reached")
	for s, m in zip(selections, metadata):
		s['metadata'] = m



