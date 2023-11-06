
from halo import Halo

MODEL = "gpt-4"


def get_metadata(selections):
	with Halo(f"generating metadata for {len(selections)} selections"):
		match MODEL:
			case 'gpt-4':
				from .gpt4 import get_metadata_gpt4
				get_metadata_gpt4(selections)
			case 'llama2':
				from .llama2 import get_metadata_llama2
				get_metadata_llama2(selections)
			case _:
				raise ValueError("Metadata MODEL is not correctly specified")
	print(f"generated {len(selections)} sets of metadata")
