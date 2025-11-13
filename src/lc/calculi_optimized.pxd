# distutils: language=c++
from libcpp.unordered_set cimport unordered_set
from libcpp.string cimport string

cdef class Term:
    cdef public unordered_set[string] free_vars
    cpdef Term subst(self, str var, Term value)
    cpdef Term reduce(self)

cdef class Var(Term):
    cdef public str name
    cpdef Term subst(self, str var, Term value)
    cpdef Term reduce(self)

cdef class App(Term):
    cdef public Term func
    cdef public Term arg
    cpdef Term subst(self, str var, Term value)
    cpdef Term reduce(self)

cdef class Abs(Term):
    cdef public str param
    cdef public Term body
    cpdef Term subst(self, str var, Term value)
    cpdef Term reduce(self)
