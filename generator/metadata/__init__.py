

MODEL = "gpt-4"


def get_metadata(selections):
    match MODEL:
        case 'gpt-4':
            from gpt4 import get_metadata_gpt4
            get_metadata_gpt4(selections)
        case 'llama2':
            raise NotImplementedError("in progress")
        case _:
            raise ValueError("Metadata MODEL is not correctly specified")



