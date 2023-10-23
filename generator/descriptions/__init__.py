
from halo import Halo

MODEL = "llama2"

def get_descriptions(n):
	with Halo(f"generating descriptions for {n} selections"):
		match MODEL:
			case 'gpt-4':
				from .gpt4 import get_descriptions_gpt4
				descs = get_descriptions_gpt4(n)
				print(f"generated {len(descs)} descriptions")
				return descs
			case 'llama2':

				from .llama2 import get_descriptions_llama2
				descs = get_descriptions_llama2(n)
				print(f"generated {len(descs)} descriptions")
				return descs
			case _:
				raise ValueError("Descriptions MODEL is not correctly specified")


