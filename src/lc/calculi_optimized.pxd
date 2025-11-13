from libc.stdint cimport uint32_t
from libcpp.unordered_set cimport unordered_set
from libcpp.string cimport string as cpp_string

cdef class Term:
    cdef uint32_t _hash
    cdef Term nf
    cdef public unordered_set[cpp_string] free_vars
    cpdef Term subst(self, cpp_string var, Term value)
    cpdef Term reduce(self)


cdef class Var(Term):
    cdef public cpp_string name
    cpdef Term subst(self, cpp_string var, Term value)
    cpdef Term reduce(self)


cdef class App(Term):
    cdef public Term func
    cdef public Term arg
    cpdef Term subst(self, cpp_string var, Term value)
    cpdef Term reduce(self)


cdef class Abs(Term):
    cdef public cpp_string param
    cdef public Term body
    cpdef Term subst(self, cpp_string var, Term value)
    cpdef Term reduce(self)
