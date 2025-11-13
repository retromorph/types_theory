import random
import string

def get_random_var_name(alphabet: str = string.ascii_lowercase + '_', length: int = 12) -> str:
    return ''.join(random.choices(alphabet, k=length))


def get_nth_lex_string(n: int, alphabet: str = string.ascii_lowercase + '_') -> str:
    k = len(alphabet)

    total = 0
    power = 1
    L = 0
    while total + power <= n:
        total += power
        L += 1
        power *= k

    idx = n - total

    res = bytearray(L)

    for i in range(L - 1, -1, -1):
        idx, r = divmod(idx, k)
        res[i] = alphabet[r]
    return res.decode()


def fresh_name(used, base="x"):
    """used: set of already existing names"""
    if base not in used:
        return base
    i = 0
    while True:
        name = f"{base}{i}"
        if name not in used:
            return name
        i += 1

