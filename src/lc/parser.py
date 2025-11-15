import re
from typing import Union
from .calculi_vanilla import Term, Var, App, Abs
from .calculi_lazy import Term as TermLazy, Var as VarLazy, App as AppLazy, Abs as AbsLazy
from .calculi_optimized import Term as TermOpt, VarFact, AppFact, AbsFact
from ..common.tokenizer import Tokenizer


VARIABLES_REGEX = r"[a-z_]+"
LC_REGEX = re.compile(rf"\s*(?:(\\)|(\.)|(\()|(\))|({VARIABLES_REGEX})|$)")


class LambdaParser:
    def __init__(self, text: str, calculi: str = 'Vanilla'):
        self.tok = Tokenizer(text, token_regex=LC_REGEX)
        self.calculi = calculi

    def parse(self) -> Union[Term, TermOpt, TermLazy]:
        term = self.parse_term()
        if self.tok.peek() is not None and self.tok.peek() != "":
            raise SyntaxError(f"Unexpected token: {self.tok.peek()}")
        return term

    def parse_term(self) -> Union[Term, TermOpt, TermLazy]:
        if self.tok.peek() == "\\":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Union[Term, TermOpt, TermLazy]:
        self.tok.next()
        param = self.tok.next()
        if not re.match(VARIABLES_REGEX, param or ""):
            raise SyntaxError(f"Expected variable after \\, got {param}")
        dot = self.tok.next()
        if dot != ".":
            raise SyntaxError(f"Expected '.', got {dot}")
        body = self.parse_term()
        if self.calculi == 'Vanilla':
            return Abs(param, body)
        elif self.calculi == 'Lazy':
            return AbsLazy(param, body)
        else:
            return AbsFact(param, body)

    def parse_app(self) -> Union[Term, TermOpt, TermLazy]:
        left = self.parse_atom()
        while True:
            nxt = self.tok.peek()
            if nxt is None or nxt in (")", "."):
                break

            if nxt == "\\":
                right = self.parse_abs()
            else:
                right = self.parse_atom()
            if self.calculi == 'Vanilla':
                left = App(left, right)
            elif self.calculi == 'Lazy':
                left = AppLazy(left, right)
            else:
                left = AppFact(left, right)
        return left

    def parse_atom(self) -> Union[Term, TermOpt, TermLazy]:
        tok = self.tok.peek()
        if tok == "(":
            self.tok.next()
            term = self.parse_term()
            if self.tok.next() != ")":
                raise SyntaxError("Expected ')'")
            return term
        elif re.match(VARIABLES_REGEX, tok or ""):
            self.tok.next()
            if self.calculi == 'Vanilla':
                return Var(tok)
            elif self.calculi == 'Lazy':
                return VarLazy(tok)
            else:
                return VarFact(tok)
        else:
            raise SyntaxError(f"Unexpected token: {tok}")
