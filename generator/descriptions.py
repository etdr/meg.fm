
from json import loads
from dotenv import dotenv_values
import openai
from openai import ChatCompletion

SYSPROMPT_VERSION = '2023-10-15'

config = dotenv_values()

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

with open(f'systemprompts/descriptions/systemprompt_{SYSPROMPT_VERSION}.txt', 'rt') as f:
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



def get_prompts(n):
    print(f"generating {n} descriptions")
    results = ChatCompletion.create(
        model="gpt-4",
        messages=get_messages(n),
        function_call={"name": "generate_music"},
        functions=[generate_music_function]
    )
    arguments = results['choices'][0]['message']['function_call']['arguments']
    prompts = loads(arguments)['prompt']
    print(f"generated {len(prompts)} descriptions")
    return prompts

