from __future__ import annotations
from typing import Union
from src.lc.calculi_optimized import Term
from dataclasses import dataclass


@dataclass(frozen=True)
class Let:
    slug: str
    body: Term

    def print(self, pretty=False) -> str:
        if pretty:
            return f"{self.slug} := ({self.body})"
        else:
            return f"{self.slug} := {self.body}"


class Line:
    def __init__(self, value: Union[Let, Term]):
        self.value = value

    def print(self, pretty=False) -> str:
        return self.value.print(pretty=pretty)


class Program:
    lines: list[Line]

    def __init__(self):
        self.lines = []

    def print(self, pretty=False) -> str:
        result = ''
        for i, line in enumerate(self.lines):
            result += line.print(pretty=pretty) + (';' if (i + 1) == len(self.lines) else '') + '\n'
        return result
