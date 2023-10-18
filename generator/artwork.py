
from base64 import b64decode
from dotenv import dotenv_values
import openai
from openai import Image, InvalidRequestError

ARTSOURCE = 'openai'

config = dotenv_values()

CONTENT_DIR = config['CONTENT_DIR']
openai.organization = config['OPENAI_ORG']
openai.api_key = config['OPENAI_KEY']


def get_artwork(selections):
    for s in selections:
        print(f"creating image for {s['uuid']}")
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
        with open(f"{CONTENT_DIR}/artwork/{s['uuid']}.png", 'wb') as f:
            f.write(image_data)