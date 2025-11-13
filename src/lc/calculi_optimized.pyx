from __future__ import annotations
import re
from .calculi_vanilla import Term as TermVan, Var as VarVan, App as AppVan, Abs as AbsVan
from ..common.utils import get_nth_lex_string, get_random_var_name, fresh_name
from libc.stdint cimport uint32_t
from typing import Dict, Tuple, Optional

_term_cache: Dict[Tuple, "Term"] = {}

cdef class Term:
    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=0):
        raise NotImplementedError("Subclasses must implement this method")

    cpdef Term subst(self, uint32_t idx, Term value):
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
            print(i)
            i += 1

        return term, i

    def from_debruijn(self, term, env=None):
        if env is None:
            env = []

        if isinstance(term, Var):
            idx = (<Var>term).idx
            if idx >= len(env):
                raise ValueError(f"Unbound DB index {idx}")
            return VarVan(env[idx])

        elif isinstance(term, App):
            return AppVan(
                self.from_debruijn((<App>term).func, env),
                self.from_debruijn((<App>term).arg, env)
            )

        elif isinstance(term, Abs):
            used = set(env)
            param = fresh_name(used)
            return AbsVan(
                param,
                self.from_debruijn(term.body, [param] + env)
            )

        else:
            raise TypeError("Unknown DB-term")

    def __str__(self) -> str:
        return self.from_debruijn(self).__str__()


cdef class Var(Term):
    def __init__(self, uint32_t idx):
        self.idx = idx

    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=0):
        return Var(self.idx + offset) if self.idx >= cutoff else self

    cpdef Term subst(self, uint32_t idx, Term value):
        return value if self.idx == idx else self

    cpdef Term reduce(self):
        return self

    def __eq__(self, other):
        return isinstance(other, Var) and self.idx == (<Var>other).idx

    def __str__(self) -> str:
        return get_nth_lex_string(self.idx)

    def __repr__(self) -> str:
        return f'{self.idx}'


cdef class App(Term):
    def __init__(self, Term func, Term arg):
        self.func = func
        self.arg = arg

    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=0):
        return App(self.func.shift(offset, cutoff), self.arg.shift(offset, cutoff))

    cpdef Term subst(self, uint32_t idx, Term value):
        return App(
            self.func.subst(idx, value),
            self.arg.subst(idx, value)
        )

    cpdef Term reduce(self):
        if isinstance(self.func, Abs):
            return (<Abs>self.func).body.subst(0, self.arg.shift(1)).shift(-1)

        cdef Term reduced_func = self.func.reduce()
        if reduced_func != self.func:
            return App(reduced_func, self.arg)

        cdef Term reduced_arg = self.arg.reduce()
        if reduced_arg != self.arg:
            return App(self.func, reduced_arg)

        return self

    def __eq__(self, other):
        return isinstance(other, App) and self.func == other.func and self.arg == other.arg

    # def __str__(self) -> str:
    #     cdef str func_str = f"({self.func})"
    #     if (isinstance(self.func, App) and isinstance((<App>self.func).func, App) and
    #         isinstance((<App>self.func).arg, App)) or isinstance(self.func, Var):
    #         func_str = re.sub(r"^\((.*)\)$", r"\1", func_str)
    #
    #     cdef str arg_str = f"({self.arg})"
    #     if isinstance(self.arg, Abs) or isinstance(self.arg, Var):
    #         arg_str = re.sub(r"^\((.*)\)$", r"\1", arg_str)
    #
    #     return f"{func_str} {arg_str}"
    #
    def __repr__(self) -> str:
        return f"({repr(self.func)} {repr(self.arg)})"


cdef class Abs(Term):
    def __init__(self, Term body):
        self.body = body

    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=0):
        return Abs(self.body.shift(offset, cutoff + 1))

    cpdef Term subst(self, uint32_t idx, Term value):
        return Abs(self.body.subst(idx + 1, value.shift(1)))

    cpdef Term reduce(self):
        return Abs(self.body.reduce())

    def __eq__(self, other):
        return isinstance(other, Abs) and self.body == other.body

    # def __str__(self) -> str:
    #     cdef str body_str = f"({self.body})"
    #     if isinstance(self.body, (App, Abs)) or isinstance(self.body, Var):
    #         body_str = re.sub(r"^\((.*)\)$", r"\1", body_str)
    #     return f"\\{self.param.decode('utf-8')}. {body_str}"
    #
    def __repr__(self) -> str:
        return f"(\\. {repr(self.body)})"
