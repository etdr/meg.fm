
from json import loads
from dotenv import dotenv_values
import openai
from openai import ChatCompletion

SYSPROMPT_VERSION = '2023-10-15'

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

with open(f'systemprompts/metadata/systemprompt_{SYSPROMPT_VERSION}.txt', 'rt') as f:
    systemprompt = f.read()

def get_messages(prompts):
    prompts_str = '\n'.join(map(lambda p: f"- {p}", prompts))
    return [
        {
            "role": "system",
            "content": systemprompt
        },
        {
            "role": "user",
            "content": f"Please generate {len(prompts)} sets of artist/title/year metadata for the given descriptions: \n{prompts_str}"
        }
    ]


def get_metadata(selections):
    print(f"generating metadata for {len(selections)} selections")
    results = ChatCompletion.create(
        model="gpt-4",
        messages=get_messages([s['prompt'] for s in selections]),
        function_call={"name": "write_metadata"},
        functions=[generate_metadata_function]
    )
    arguments = results['choices'][0]['message']['function_call']['arguments']
    metadata = loads(arguments)['metadata']
    for s, m in zip(selections, metadata):
        s['metadata'] = m
