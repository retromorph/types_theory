from __future__ import annotations
import re
from dataclasses import dataclass
from abc import ABC


class Term(ABC):
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


@dataclass(frozen=True)
class Var(Term):
    name: str


@dataclass(frozen=True)
class App(Term):
    func: Term
    arg: Term


@dataclass(frozen=True)
class Abs(Term):
    param: str
    body: Term
