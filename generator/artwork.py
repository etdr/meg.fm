
from base64 import b64decode
from io import BytesIO
from os import devnull
from subprocess import run, DEVNULL
from contextlib import redirect_stdout
from dotenv import dotenv_values


ARTSOURCE = "sdxl"

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']


def get_artwork(selections):
	match ARTSOURCE:
		case 'openai':
			get_artwork_openai(selections)
		case 'sdxl':
			get_artwork_sdxl(selections)
		case _:
			raise ValueError("ARTSOURCE is not correctly specified")


def get_artwork_openai(selections):
	import openai
	from openai import Image, InvalidRequestError
	openai.organization = config['OPENAI_ORG']
	openai.api_key = config['OPENAI_KEY']

	for s in selections:
		print(f"creating image for {s['uuid']}...  ", end='')
		try:
			response = Image.create(
				prompt=f"Album art for the song \"{s['metadata']['title']}\", by the artist {s['metadata']['artist']}, from the year {s['metadata']['year']}. Avoid text! The music sounds like this: {s['description']}",
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
		print(f"writing {len(image_data) / (1024 ** 2):<3.3}MB...  ", end='')
		write_files(s['uuid'], image_data)



def get_artwork_sdxl(selections):
	# from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
	# pipeline = StableDiffusionXLPipeline.from_pretrained(
	#     "stabilityai/stable-diffusion-xl-base-1.0").to("cuda")
	# refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
	#     "stabilityai/stable-diffusion-xl-refiner-1.0").to("cuda")

	from torch import float16
	from diffusers import DiffusionPipeline

	# with open(devnull, 'w') as fnull, redirect_stdout(fnull):
	base = DiffusionPipeline.from_pretrained(
		"stabilityai/stable-diffusion-xl-base-1.0",
		torch_dtype=float16,
		variant='fp16',
		use_safetensors=True
	).to("cuda")
	base.set_progress_bar_config(leave=False)
	refiner = DiffusionPipeline.from_pretrained(
		"stabilityai/stable-diffusion-xl-refiner-1.0",
		text_encoder_2=base.text_encoder_2,
		vae=base.vae,
		torch_dtype=float16,
		variant='fp16',
		use_safetensors=True
	).to("cuda")
	refiner.set_progress_bar_config(leave=False)
	
	for s in selections:
		print(f"creating image for {s['uuid']}...  ", end='', flush=True)
		try:
			prompt = f"Album art for the song \"{s['metadata']['title']}\", by the artist {s['metadata']['artist']}, from the year {s['metadata']['year']}, the music sounds like {s['description']}"
		except KeyError:
			continue
		with open(devnull, 'w') as fnull, redirect_stdout(fnull):
			image = base(
				prompt=prompt,
				num_inference_steps=50,
				denoising_end=0.8,
				output_type='latent'
			).images
			image = refiner(
				prompt=prompt,
				num_inference_steps=50,
				denoising_start=0.8,
				image=image
			).images[0]
	
		image_bytes = BytesIO()
		image.save(image_bytes, format='png')
		print(f"writing {image_bytes.tell() / (1024 ** 2):<3.3}MB...  ", end='', flush=True)
		image_bytes.seek(0)
		write_files(s['uuid'], image_bytes.read())
	

def write_files(uuid, data):
	with open(f"{CONTENT_DIR}/artwork/png/{uuid}.png", 'wb') as f:
		f.write(data)
	run([
		"cwebp",
		"-q", "80",
		f"{CONTENT_DIR}/artwork/png/{uuid}.png",
		"-o", f"{CONTENT_DIR}/artwork/webp/{uuid}.webp"
	], stdout=DEVNULL, stderr=DEVNULL)
	print("✔")



	