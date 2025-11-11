import random
import string
from .primitives import Term, Var, App, Abs


def get_unique_var_name() -> str:
    return ''.join(random.choices(string.ascii_lowercase + '_', k=12))

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
        elif var not in term.body.free_vars or term.param not in value.free_vars:
            return Abs(term.param, subst(term.body, var, value))
        else:
            new_variable = get_unique_var_name()
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

        if i % 10000 == 0:
            print(f"Normalization step = {i}")

    if trace:
        print(f"Normalized with steps = {i}")
    return term
