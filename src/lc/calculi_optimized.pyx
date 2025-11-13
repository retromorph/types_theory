from __future__ import annotations
import re
from ..common.utils import get_nth_lex_string, get_random_var_name
from libcpp.unordered_set cimport unordered_set
from libcpp.string cimport string as cpp_string
from typing import Dict, Tuple

_term_cache: Dict[Tuple, "Term"] = {}

cdef class Term:
    def __init__(self):
        self._hash = 0
        self.nf = None

    def __hash__(self) -> int:
        return self._hash

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
        super().__init__()
        self.name = cpp_string(name.encode())
        self.free_vars = unordered_set[cpp_string]()
        self.free_vars.insert(self.name)
        self._hash = hash(("v", name))

    cpdef Term subst(self, cpp_string var, Term value):
        return value if self.name == var else self

    cpdef Term reduce(self):
        return self

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == (<Var>other).name

    def __str__(self) -> str:
        return self.name.decode('utf-8')

    def __repr__(self) -> str:
        return self.name.decode('utf-8')


def VarFact(name: str) -> Var:
    key = ("v", name)
    t = _term_cache.get(key)
    if t is None:
        t = Var(name)
        _term_cache[key] = t
    return t


cdef class App(Term):
    def __init__(self, Term func, Term arg):
        super().__init__()
        self.func = func
        self.arg = arg
        self._hash = hash(("a", func, arg))
        self.free_vars = unordered_set[cpp_string]()

        cdef cpp_string cpp_var
        for cpp_var in func.free_vars:
            self.free_vars.insert(cpp_var)
        for cpp_var in arg.free_vars:
            self.free_vars.insert(cpp_var)

    cpdef Term subst(self, cpp_string var, Term value):
        return AppFact(
            self.func.subst(var, value),
            self.arg.subst(var, value)
        )

    cpdef Term reduce(self):
        if self.nf is not None:
            return self.nf

        if isinstance(self.func, Abs):
            self.nf = (<Abs>self.func).body.subst((<Abs>self.func).param, self.arg).reduce()
            return self.nf

        cdef Term reduced_func = self.func.reduce()
        if reduced_func != self.func:
            return AppFact(reduced_func, self.arg)

        cdef Term reduced_arg = self.arg.reduce()
        if reduced_arg != self.arg:
            return AppFact(self.func, reduced_arg)

        return self

    def __hash__(self) -> int:
        return self._hash

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


def AppFact(f: Term, a: Term) -> App:
    key = ("a", f, a)
    t = _term_cache.get(key)
    if t is None:
        t = App(f, a)
        _term_cache[key] = t
    return t


cdef class Abs(Term):
    def __init__(self, str param, Term body):
        super().__init__()
        self.param = cpp_string(param.encode())
        self.body = body
        self._hash = hash(("l", param, body))
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
            return AbsFact(
                self.param.decode('utf-8'),
                self.body.subst(var, value)
            )

        cdef str new_variable = get_random_var_name()
        cdef cpp_string cpp_new_variable = cpp_string(new_variable.encode())
        cdef Term alpha_step = self.body.subst(self.param, VarFact(new_variable))
        cdef Term subst_step = alpha_step.subst(var, value)
        return AbsFact(
            new_variable,
            subst_step
        )

    cpdef Term reduce(self):
        if self.nf is not None:
            return self.nf

        body_nf = self.body.reduce()
        if body_nf is self.body:
            nf = self
        else:
            nf = AbsFact(self.param.decode('utf-8'), body_nf)
        self.nf = nf
        return nf

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other):
        return isinstance(other, Abs) and self.body == other.body

    def __str__(self) -> str:
        cdef str body_str = f"({self.body})"
        if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
            body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
        return f"\\{self.param.decode('utf-8')}. {body_str}"

    def __repr__(self) -> str:
        return f"(\\{self.param.decode('utf-8')}. {repr(self.body)})"


def AbsFact(param: str, body: Term) -> Abs:
    key = ("l", param, body)
    t = _term_cache.get(key)
    if t is None:
        t = Abs(param, body)
        _term_cache[key] = t
    return t
