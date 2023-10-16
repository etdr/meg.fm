
from uuid import uuid4
from datetime import datetime
from ruamel.yaml import YAML

from descriptions import get_prompts, SYSPROMPT_VERSION as PROMPT_SYSP_VER
from music import generate_music
from metadata import get_metadata, SYSPROMPT_VERSION as META_SYSP_VER
from artwork import get_artwork #, SYSPROMPT_VERSION as ART_SYSP_VER

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)



def generate_tracks(n):
    timestamp = datetime.now().isoformat()
    print(f"starting generation of {n} objects at ${timestamp}")

    prompts_list = get_prompts(n)

    selections = [
        {
            'uuid': str(uuid4()),
            'prompt': p,
            'created': timestamp,
            'sysprompt_versions': {
                'prompt': PROMPT_SYSP_VER,
                'metadata': META_SYSP_VER,
                # 'artwork': ART_SYSP_VER
            }
        }
        for p
        in prompts_list
    ]

    generate_music(selections)
    get_metadata(selections)
    get_artwork(selections)

    for s in selections:
        with open(f"../content/info/{s['uuid']}.yaml", 'wt') as f:
            yaml.dump(s, f)
        


