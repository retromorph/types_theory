import itertools
import random
import string
from .primitives import Term, Var, App, Abs


def free_vars(term: Term) -> set[str]:
    if isinstance(term, Var):
        return {term.name}
    elif isinstance(term, App):
        return free_vars(term.func).union(free_vars(term.arg))
    elif isinstance(term, Abs):
        result = free_vars(term.body)
        result.discard(term.param)
        return result
    return set()


def get_unique_var_name(names: set[str]) -> str:
    # alphabet = string.ascii_lowercase
    # n = 1
    # while True:
    #     for s in map(''.join, itertools.product(alphabet, repeat=n)):
    #         if s not in names:
    #             return s
    #     n += 1
    return ''.join(random.choices(string.ascii_lowercase, k=10))


def subst(term: Term, var: str, value: Term) -> Term:
    if isinstance(term, Var):
        if term.name == var:
            return value
        return term
    elif isinstance(term, App):
        return App(subst(term.func, var, value), subst(term.arg, var, value))
    elif isinstance(term, Abs):
        if term.param == var:
            return term
        elif var not in free_vars(term.body) or term.param not in free_vars(value):
            return Abs(term.param, subst(term.body, var, value))
        else:
            new_variable = get_unique_var_name(free_vars(term).union(free_vars(value)))
            first_step = subst(term.body, term.param, Var(new_variable))
            second_step = subst(first_step, var, value)
            return Abs(new_variable, second_step)
    return term


def beta_reduce(term: Term) -> Term:
    if isinstance(term, App) and isinstance(term.func, Abs):
        return subst(term.func.body, term.func.param, term.arg)

    elif isinstance(term, App):
        reduced_func = beta_reduce(term.func)
        if reduced_func != term.func:
            return App(reduced_func, term.arg)
        reduced_arg = beta_reduce(term.arg)
        if reduced_arg != term.arg:
            return App(term.func, reduced_arg)
        return term

    elif isinstance(term, Abs):
        reduced_body = beta_reduce(term.body)
        return Abs(term.param, reduced_body)

    else:
        return term


def normalize(term: Term, n_steps=None, trace=False) -> Term:
    prev = None
    i = 0
    while term != prev:
        if n_steps is not None and i == n_steps:
            break
        prev = term
        term = beta_reduce(term)
        i += 1

    if trace:
        print(f"Normalized with steps = {i}")
    return term
