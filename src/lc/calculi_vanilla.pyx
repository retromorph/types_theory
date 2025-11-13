from __future__ import annotations
import re
from ..common.utils import get_random_var_name
from libcpp.unordered_set cimport unordered_set
from libcpp.string cimport string as cpp_string


cdef class Term:
    cpdef Term subst(self, cpp_string var, Term value):
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
        self.name = cpp_string(name.encode())
        self.free_vars = unordered_set[cpp_string]()
        self.free_vars.insert(self.name)

    cpdef Term subst(self, cpp_string var, Term value):
        if self.name == var:
            return value
        return self

    cpdef Term reduce(self):
        return self

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == (<Var>other).name

    def __str__(self) -> str:
        return self.name.decode('utf-8')

    def __repr__(self) -> str:
        return self.name.decode('utf-8')


cdef class App(Term):
    def __init__(self, Term func, Term arg):
        self.func = func
        self.arg = arg
        self.free_vars = unordered_set[cpp_string]()

        cdef cpp_string cpp_var
        for cpp_var in func.free_vars:
            self.free_vars.insert(cpp_var)
        for cpp_var in arg.free_vars:
            self.free_vars.insert(cpp_var)

    cpdef Term subst(self, cpp_string var, Term value):
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
        self.param = cpp_string(param.encode())
        self.body = body
        self.free_vars = unordered_set[cpp_string]()

        cdef cpp_string cpp_var
        for cpp_var in body.free_vars:
            if cpp_var != self.param:
                self.free_vars.insert(cpp_var)

    cpdef Term subst(self, cpp_string var, Term value):
        if self.param == var:
            return self
        elif self.body.free_vars.count(var) == 0 and value.free_vars.count(self.param) == 0:
            return self
        elif self.body.free_vars.count(var) == 0 or value.free_vars.count(self.param) == 0:
            return Abs(
                self.param.decode('utf-8'),
                self.body.subst(var, value)
            )

        cdef str new_variable = get_random_var_name()
        cdef cpp_string cpp_new_variable = cpp_string(new_variable.encode())
        cdef Term alpha_step = self.body.subst(self.param, Var(new_variable))
        cdef Term subst_step = alpha_step.subst(var, value)
        return Abs(
            new_variable,
            subst_step
        )

    cpdef Term reduce(self):
        return Abs(self.param.decode('utf-8'), self.body.reduce())

    def __eq__(self, other):
        return isinstance(other, Abs) and self.param == (<Abs>other).param and self.body == other.body

    def __str__(self) -> str:
        cdef str body_str = f"({self.body})"
        if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
            body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
        return f"\\{self.param.decode('utf-8')}. {body_str}"

    def __repr__(self) -> str:
        return f"(\\{self.param.decode('utf-8')}. {repr(self.body)})"
