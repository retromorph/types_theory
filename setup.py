from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize


setup(
    name="types_theory",
    version="0.1",
    packages=find_packages(),
    ext_modules=cythonize(
        ["src/lc/calculi_vanilla.pyx", "src/lc/calculi_optimized.pyx"],
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "nonecheck": False,
            "cdivision": True,
            "overflowcheck": False,
            "infer_types": False,
            "c_string_type": "bytes",
            "c_string_encoding": "utf-8",
            "warn.undeclared": True,
            "warn.unreachable": True,
            # debug
            "profile": True
        },
        language='c++'
    ),
    zip_safe=False,
)
