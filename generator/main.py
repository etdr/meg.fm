#!/usr/bin/env python3

from uuid import uuid4
from datetime import datetime
from argparse import ArgumentParser
from dotenv import dotenv_values
from pynput import keyboard
from ruamel.yaml import YAML

from utils import banner, printline
from descriptions import get_descriptions, \
    SYSPROMPT_VERSION as PROMPT_SYSP_VER
from music import generate_music
from metadata import get_metadata
    # SYSPROMPT_VERSION as META_SYSP_VER
    # MODEL as METADATA_MODEL
from artwork import get_artwork, ARTSOURCE

config = dotenv_values()
CONTENT_DIR = config['CONTENT_DIR']

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def generate_tracks(n, batch_num=0):
    time_start = datetime.now()
    print(f"starting generation of {n} objects at {time_start.isoformat()}")

    descs_list = get_descriptions(n)

    selections = [
        {
            'uuid': str(uuid4()),
            'description': d,
            'created': time_start,
            'sysprompt_versions': {
                'prompt': PROMPT_SYSP_VER
                # 'metadata': META_SYSP_VER,
                # 'artwork': ART_SYSP_VER
            },
            'artwork': {
                'source': ARTSOURCE
            }
        }
        for d
        in descs_list
    ]

    get_metadata(selections)
    get_artwork(selections)
    generate_music(selections)

    for s in selections:
        with open(f"{CONTENT_DIR}/info/{s['uuid']}.yaml", 'wt') as f:
            yaml.dump(s, f)

    time_end = datetime.now()
    runtime_mins = (time_end - time_start).seconds / 60
    print(f"{f'BATCH {batch_num}: ' if batch_num != 0 else ''}generated {len(selections)} tracks in {runtime_mins:<4.4} minutes")
    print(f"roughly {len(selections) / runtime_mins:<3.3} tracks per minute")
    return len(selections)


def batch_generate_tracks(batches, batch_size):
    num_generated = 0
    for i in range(batches):
        banner(f"COMMENCING WITH BATCH {i + 1} OF {batches}", 1)
        num_generated += generate_tracks(batch_size, i + 1)
    return num_generated


if __name__ == "__main__":
    parser = ArgumentParser(description="generates batches of hypothetical music and associated data")
    parser.add_argument("n", type=int, help="number of tracks to generate per batch")
    parser.add_argument("-b", "--batches", type=int, help="number of batches", default=1)
    parser.add_argument("-u", "--until", type=str, help="time to generate until", default='')
    # add arguments (when applicable) for:
    #   - description model selection
    #   - metadata model selection
    #   - artwork model selection
    args = parser.parse_args()

    if args.until:
        time_until = datetime.fromisoformat(args.until)
    else:
        time_until = datetime.max
    time_start = datetime.now()

    exit_generation = False
    def stop_after_this(k):
        global exit_generation
        if k == keyboard.Key.esc:
            exit_generation = True
            print("exiting after current batch")
    key_listener = keyboard.Listener(on_press=stop_after_this)
    key_listener.start()

    if args.until:
        num_generated = 0
        banner("STARTING UNTIL RUN", 0)
        while not exit_generation and datetime.now() < time_until:
            banner("EXIT TIME NOT REACHED, COMMENCING SINGLE BATCH")
            num_generated += generate_tracks(args.n)
    else:
        while not exit_generation:
            if args.batches == 1:
                banner("COMMENCING WITH SINGLE BATCH", 0)
                num_generated = generate_tracks(args.n)
                break
            else:
                banner(f"STARTING RUN OF {args.batches} BATCHES", 0)
                num_generated = batch_generate_tracks(args.batches, args.n)
                break
    
    key_listener.stop()
    time_end = datetime.now()
    runtime_mins = (time_end - time_start).seconds / 60
    printline(1)
    if exit_generation:
        print("Exiting on request")
    print(f"TOTAL RUN: generated {num_generated} tracks in {runtime_mins:<4.4} minutes")
    print(f"roughly {num_generated / runtime_mins:<3.3} tracks per minute")
    banner("GENERATION COMPLETE! 💯", 0)
