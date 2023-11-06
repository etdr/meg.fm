
import os
from subprocess import run, DEVNULL
from contextlib import redirect_stdout, redirect_stderr
from warnings import catch_warnings, simplefilter
from torch.cuda import empty_cache as torch_empty_cache
from gc import collect as gccollect
from halo import Halo
from dotenv import dotenv_values

from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

SUBSET_SIZE = 8

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']


def generate_subset(model, descriptions, start_idx):
	print(f"generating music for ids:")
	for i, p in enumerate(descriptions):
		print(f"{i + start_idx:03} • {p['uuid']}".rjust(4))
	return model.generate((p['description'] for p in descriptions), progress=True)


# TODO: Add better index printing

def generate_music(descriptions):

	with catch_warnings():
		simplefilter("ignore")
		model = MusicGen.get_pretrained("facebook/musicgen-large")
	model.set_generation_params(duration=60)

	# doing five at a time so we don't run out of memory
	wavsets = [
		generate_subset(model, ps, start_idx)
		for start_idx, ps
		in [(i, descriptions[i:i + SUBSET_SIZE])
			for i
			in range(0, len(descriptions), SUBSET_SIZE)]
	]

	sr = model.sample_rate
	del model
	torch_empty_cache()
	gccollect()

	wavs = [w for ws in wavsets for w in ws]
	music = zip((p['uuid'] for p in descriptions), wavs)
	with Halo(f"converting {len(descriptions)} wavs to opus"):
		for selection in music:
			filename = f"{CONTENT_DIR}/music/{selection[0]}"
			# print(f'writing wav file for selection {selection[0]}')
			with open(os.devnull, 'w') as fnull, redirect_stdout(fnull), redirect_stderr(fnull):
				audio_write(
					filename,
					selection[1].cpu(),
					sr,
					strategy='loudness'
				)
			run([
				"ffmpeg",
				"-i", f"{filename}.wav",
				"-c:a", "libopus",
				"-b:a", "160k",
				"-application", "audio",
				f"{filename}.opus"
			], stdout=DEVNULL, stderr=DEVNULL)
			os.remove(f"{filename}.wav")

