# This file is a wrapper around the Cython implementation
# It imports and re-exports the classes from the compiled Cython module

try:
    # Try to import from the compiled Cython module
    from .calculi_vanilla import Term, Var, App, Abs
except ImportError:
    # If the Cython module is not available, use the original Python implementation
    import re
    from abc import ABC, abstractmethod
    from ..common.utils import get_random_var_name

    class Term(ABC):
        free_vars: set[str]

        @abstractmethod
        def subst(self, var: str, value: 'Term') -> 'Term':
            pass

        @abstractmethod
        def reduce(self) -> 'Term':
            pass

        def normalize(self, n_steps: int=-1) -> ('Term', int):
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
            self.free_vars = {name}

        def subst(self, var: str, value: 'Term') -> 'Term':
            if self.name == var:
                return value
            return self

        def reduce(self) -> 'Term':
            return self

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
            self.free_vars = func.free_vars | arg.free_vars

        def subst(self, var: str, value: 'Term') -> 'Term':
            return App(
                self.func.subst(var, value),
                self.arg.subst(var, value)
            )

        def reduce(self) -> 'Term':
            if isinstance(self.func, Abs):
                return self.func.body.subst(self.func.param, self.arg)

            reduced_func = self.func.reduce()
            if reduced_func != self.func:
                return App(reduced_func, self.arg)

            reduced_arg = self.arg.reduce()
            if reduced_arg != self.arg:
                return App(self.func, reduced_arg)

            return self

        def __eq__(self, other):
            return isinstance(other, App) and self.func == other.func and self.arg == other.arg

        def __str__(self) -> str:
            func_str = f"({self.func})"
            if (isinstance(self.func, App) and isinstance(self.func.func, App) and isinstance(self.func.arg, App)) or isinstance(self.func, Var):
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
            self.free_vars = body.free_vars - {param}

        def subst(self, var: str, value: 'Term') -> 'Term':
            if self.param == var:
                return self
            elif var not in self.body.free_vars and self.param not in value.free_vars:
                return self
            elif var not in self.body.free_vars or self.param not in value.free_vars:
                return Abs(
                    self.param,
                    self.body.subst(var, value)
                )

            new_variable = get_random_var_name()
            alpha_step = self.body.subst(self.param, Var(new_variable))
            subst_step = alpha_step.subst(var, value)
            return Abs(
                new_variable,
                subst_step
            )

        def reduce(self) -> 'Term':
            return Abs(self.param, self.body.reduce())

        def __eq__(self, other):
            return isinstance(other, Abs) and self.param == other.param and self.body == other.body

        def __str__(self) -> str:
            body_str = f"({self.body})"
            if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
                body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
            return f"\\{self.param}. {body_str}"

        def __repr__(self) -> str:
            return f"(\\{self.param}. {repr(self.body)})"
