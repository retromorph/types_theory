import re
from abc import ABC, abstractmethod
from ..common.utils import get_random_var_name


class Node:
    __slots__ = ("kind", "var", "body", "func", "arg", "free_vars")

    def __init__(self, kind, var=None, body=None, func=None, arg=None):
        self.kind = kind
        self.var = var
        self.body = body
        self.func = func
        self.arg = arg
        if kind == 0:
            self.free_vars = {var}
        elif kind == 1:
            self.free_vars = func.free_vars | arg.free_vars
        else:
            self.free_vars = body.free_vars - {var}

    def subst(self, var: str, value: 'Node') -> 'Node':
        if self.kind == 0:
            if self.var == var:
                return value
            return self
        elif self.kind == 1:
            return Node(
                1,
                func=self.func.subst(var, value),
                arg=self.arg.subst(var, value)
            )
        else:
            if self.var == var:
                return self
            elif var not in self.body.free_vars and self.var not in value.free_vars:
                return self
            elif var not in self.body.free_vars or self.var not in value.free_vars:
                return Node(
                    2,
                    var=self.var,
                    body=self.body.subst(var, value)
                )

            new_variable = get_random_var_name()
            alpha_step = self.body.subst(self.var, Node(0, var=new_variable))
            subst_step = alpha_step.subst(var, value)
            return Node(
                2,
                var=new_variable,
                body=subst_step
            )

    def reduce(self) -> 'Node':
        if self.kind == 0:
            return self
        elif self.kind == 1:
            if self.func.kind == 2:
                return self.func.body.subst(self.func.var, self.arg)

            reduced_func = self.func.reduce()
            if reduced_func != self.func:
                return Node(1, func=reduced_func, arg=self.arg)

            reduced_arg = self.arg.reduce()
            if reduced_arg != self.arg:
                return Node(1, func=self.func, arg=reduced_arg)

            return self
        else:
            return Node(2, var=self.var, body=self.body.reduce())


class Term(ABC):
    free_vars: set[str]

    @abstractmethod
    def subst(self, var: str, value: 'Term') -> 'Term':
        pass

    @abstractmethod
    def reduce(self) -> 'Term':
        pass

    def normalize(self, n_steps: int = -1) -> ('Term', int):
        term = self
        prev = None
        i = 0
        while term != prev:
            if -1 < n_steps == i:
                break
            prev = term
            term = term.reduce()
            i += 1
        return term, i


class Var(Term):
    name: str

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class App(Term):
    func: 'Term'
    arg: 'Term'

    def __init__(self, func: 'Term', arg: 'Term'):
        self.func = func
        self.arg = arg

    def __eq__(self, other):
        return isinstance(other, App) and self.func == other.func and self.arg == other.arg

    def __str__(self) -> str:
        func_str = f"({self.func})"
        if (isinstance(self.func, App) and isinstance(self.func.func, App) and isinstance(self.func.arg,
                                                                                          App)) or isinstance(self.func,
                                                                                                              Var):
            func_str = re.sub(r"^\((.*)\)$", r"\1", func_str)

        arg_str = f"({self.arg})"
        if isinstance(self.arg, Abs) or isinstance(self.arg, Var):
            arg_str = re.sub(r"^\((.*)\)$", r"\1", arg_str)

        return f"{func_str} {arg_str}"

    def __repr__(self) -> str:
        return f"({repr(self.func)} {repr(self.arg)})"


class Abs(Term):
    param: str
    body: 'Term'

    def __init__(self, param: str, body: 'Term'):
        self.param = param
        self.body = body

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == other.param and self.body == other.body

    def __str__(self) -> str:
        body_str = f"({self.body})"
        if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
            body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
        return f"\\{self.param}. {body_str}"

    def __repr__(self) -> str:
        return f"(\\{self.param}. {repr(self.body)})"
