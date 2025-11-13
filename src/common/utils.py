import random
import string

def get_random_var_name(alphabet: str = string.ascii_lowercase + '_', length: int = 12) -> str:
    return ''.join(random.choices(alphabet, k=length))
