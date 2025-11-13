from __future__ import annotations
import re
from ..common.utils import get_random_var_name

cdef class Term:
    cpdef Term subst(self, str var, Term value):
        raise NotImplementedError("Subclasses must implement this method")

    cpdef Term reduce(self):
        raise NotImplementedError("Subclasses must implement this method")

    def normalize(self, int n_steps=-1) -> tuple[Term, int]:
        cdef Term term = self
        cdef Term prev = None
        cdef int i = 0

        while term != prev:
            if -1 < n_steps == i:
                break
            prev = term
            term = term.reduce()
            i += 1

        return term, i


cdef class Var(Term):
    def __init__(self, str name):
        self.name = name
        self.free_vars = {name}

    cpdef Term subst(self, str var, Term value):
        if self.name == var:
            return value
        return self

    cpdef Term reduce(self):
        return self

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


cdef class App(Term):
    def __init__(self, Term func, Term arg):
        self.func = func
        self.arg = arg
        self.free_vars = func.free_vars | arg.free_vars

    cpdef Term subst(self, str var, Term value):
        return App(
            self.func.subst(var, value),
            self.arg.subst(var, value)
        )

    cpdef Term reduce(self):
        if isinstance(self.func, Abs):
            return (<Abs>self.func).body.subst((<Abs>self.func).param, self.arg)

        cdef Term reduced_func = self.func.reduce()
        if reduced_func != self.func:
            return App(reduced_func, self.arg)

        cdef Term reduced_arg = self.arg.reduce()
        if reduced_arg != self.arg:
            return App(self.func, reduced_arg)

        return self

    def __eq__(self, other):
        return isinstance(other, App) and self.func == other.func and self.arg == other.arg

    def __str__(self) -> str:
        cdef str func_str = f"({self.func})"
        if (isinstance(self.func, App) and isinstance((<App>self.func).func, App) and 
            isinstance((<App>self.func).arg, App)) or isinstance(self.func, Var):
            func_str = re.sub(r"^\((.*)\)$", r"\1", func_str)

        cdef str arg_str = f"({self.arg})"
        if isinstance(self.arg, Abs) or isinstance(self.arg, Var):
            arg_str = re.sub(r"^\((.*)\)$", r"\1", arg_str)

        return f"{func_str} {arg_str}"

    def __repr__(self) -> str:
        return f"({repr(self.func)} {repr(self.arg)})"


cdef class Abs(Term):
    def __init__(self, str param, Term body):
        self.param = param
        self.body = body
        self.free_vars = body.free_vars - {param}

    cpdef Term subst(self, str var, Term value):
        if self.param == var:
            return self
        elif var not in self.body.free_vars and self.param not in value.free_vars:
            return self
        elif var not in self.body.free_vars or self.param not in value.free_vars:
            return Abs(
                self.param,
                self.body.subst(var, value)
            )

        cdef str new_variable = get_random_var_name()
        cdef Term alpha_step = self.body.subst(self.param, Var(new_variable))
        cdef Term subst_step = alpha_step.subst(var, value)
        return Abs(
            new_variable,
            subst_step
        )

    cpdef Term reduce(self):
        return Abs(self.param, self.body.reduce())

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == other.param and self.body == other.body

    def __str__(self) -> str:
        cdef str body_str = f"({self.body})"
        if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
            body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
        return f"\\{self.param}. {body_str}"

    def __repr__(self) -> str:
        return f"(\\{self.param}. {repr(self.body)})"
