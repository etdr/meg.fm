
from base64 import b64decode
from dotenv import dotenv_values
import openai
from openai import Image, InvalidRequestError

SYSPROMPT_VERSION = '2023-10-15'

conf = dotenv_values()

openai.organization = conf['OPENAI_ORG']
openai.api_key = conf['OPENAI_KEY']


def get_artwork(selections):
    for s in selections:
        try:
            response = Image.create(
                prompt=f"Album art for the song \"{s['metadata']['title']}\", by the artist {s['metadata']['artist']}, from the year {s['metadata']['year']}. Avoid text! The music sounds like this: {s['prompt']}",
                n=1,
                size='1024x1024',
                response_format='b64_json'
            )
        except InvalidRequestError:
            response = Image.create(
                prompt="Album art for a piece of music. No text. In any style you want.",
                n=1,
                size='1024x1024',
                response_format='b64_json'
            )
        image_data = b64decode(response['data'][0]['b64_json'])
        with open(f"../content/artwork/{s['uuid']}.png", 'wb') as f:
            f.write(image_data)