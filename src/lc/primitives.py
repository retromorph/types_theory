from __future__ import annotations
import re
from abc import ABC
from typing import Dict, Optional


class Term(ABC):
    free_vars: set[str]

    def print(self, pretty=False) -> str:
        def print_step(term: Term) -> tuple[str, str]:
            if isinstance(term, Var):
                return term.name, Var.__name__
            elif isinstance(term, App):
                func, func_type = print_step(term.func)
                if pretty and func_type == App.__name__:
                    func = re.sub(r'^\((.*)\)$', r'\1', func)
                arg, arg_type = print_step(term.arg)
                if pretty and arg_type == Abs.__name__:
                    arg = re.sub(r'^\((.*)\)$', r'\1', arg)
                return f"({func} {arg})", App.__name__
            elif isinstance(term, Abs):
                param = term.param
                body, body_type = print_step(term.body)
                if pretty and body_type in (App.__name__, Abs.__name__):
                    body = re.sub(r'^\((.*)\)$', r'\1', body)
                return f"(\\{param}. {body})", Abs.__name__

            raise ValueError(f"Unexpected term type: {type(term)}")

        result, _ = print_step(self)
        if pretty:
            result = re.sub(r'^\((.*)\)$', r'\1', result)
        return result


class Var(Term):
    name: str

    def __init__(self, name: str):
        self.name = name
        self.free_vars = {name}

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name


class App(Term):
    func: Term
    arg: Term

    def __init__(self, func: Term, arg: Term):
        self.func = func
        self.arg = arg
        self.free_vars = func.free_vars | arg.free_vars

    def __eq__(self, other):
        if not isinstance(other, App):
            return NotImplemented
        return isinstance(other, App) and self.func == other.func and self.arg == other.arg


class Abs(Term):
    param: str
    body: Term

    def __init__(self, param: str, body: Term, env: Optional[Dict[str, "Thunk"]] = None):
        self.param = param
        self.body = body
        self.free_vars = body.free_vars.copy() - {param}
        self.env = env

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == other.param and self.body == other.body
