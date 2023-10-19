
from uuid import uuid4
from datetime import datetime
from argparse import ArgumentParser
from dotenv import dotenv_values
from ruamel.yaml import YAML

from utils import gtw
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


def generate_tracks(n):
    timestamp = datetime.now().isoformat()
    print(f"starting generation of {n} objects at {timestamp}")

    descs_list = get_descriptions(n)

    selections = [
        {
            'uuid': str(uuid4()),
            'description': d,
            'created': timestamp,
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

    generate_music(selections)
    get_metadata(selections)
    get_artwork(selections)

    for s in selections:
        with open(f"{CONTENT_DIR}/info/{s['uuid']}.yaml", 'wt') as f:
            yaml.dump(s, f)
        


def batch_generate_tracks(batches, batch_size):
    for i in range(batches):
        print(f"──────────────── COMMENCING WITH BATCH {i + 1} OF {batches} ".ljust(gtw(), '─'))
        generate_tracks(batch_size)


if __name__ == "__main__":
    parser = ArgumentParser(description="generates batches of hypothetical music and associated data")
    parser.add_argument("n", type=int, help="number of tracks to generate per batch")
    parser.add_argument("-b", "--batches", type=int, help="number of batches", default=1)
    # add argument for artwork generator selection
    args = parser.parse_args()

    if args.batches == 1:
        print(f"──────────────── COMMENCING WITH SINGLE BATCH ".ljust(gtw(), '─'))
        generate_tracks(args.n)
    else:
        print(f"════════════════ STARTING RUN OF {args.batches} BATCHES ".ljust(gtw(), '═'))
        batch_generate_tracks(args.batches, args.n)
    
    print(f"════════════════ GENERATION COMPLETE! 💯 ".ljust(gtw(), '═'))