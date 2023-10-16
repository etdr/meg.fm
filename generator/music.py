
import os
from subprocess import run
import soundfile as sf
import numpy as np
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

model = MusicGen.get_pretrained("facebook/musicgen-large")
model.set_generation_params(duration=60)


def generate_music(prompts):
    wavs = model.generate(p['prompt'] for p in prompts)
    music = zip((p['uuid'] for p in prompts), wavs)
    for selection in music:
        filename = f"../content/music/{selection[0]}"
        # print(f'writing wav file for selection {selection[0]}')
        audio_write(
            filename,
            selection[1].cpu(),
            model.sample_rate,
            strategy='loudness'
        )
        run([
            "ffmpeg",
            "-i", f"{filename}.wav",
            "-c:a", "libopus",
            "-b:a", "160k",
            "-application", "audio",
            f"{filename}.opus"
        ])
        os.remove(f"{filename}.wav")

