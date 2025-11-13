from libc.stdint cimport uint32_t

cdef class Term:
    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=*)
    cpdef Term subst(self, uint32_t idx, Term value)
    cpdef Term reduce(self)


cdef class Var(Term):
    cdef public uint32_t idx
    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=*)
    cpdef Term subst(self, uint32_t idx, Term value)
    cpdef Term reduce(self)


cdef class App(Term):
    cdef public Term func
    cdef public Term arg
    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=*)
    cpdef Term subst(self, uint32_t idx, Term value)
    cpdef Term reduce(self)


cdef class Abs(Term):
    cdef public Term body
    cpdef Term shift(self, uint32_t offset, uint32_t cutoff=*)
    cpdef Term subst(self, uint32_t idx, Term value)
    cpdef Term reduce(self)
