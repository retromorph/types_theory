import re
from .calculi_vanilla import Term, Var, App, Abs
from ..common.tokenizer import Tokenizer

VARIABLES_REGEX = r"[a-z_]+"
LC_REGEX = re.compile(rf"\s*(?:(\\)|(\.)|(\()|(\))|({VARIABLES_REGEX})|$)")


class LambdaParser:
    def __init__(self, text):
        self.tok = Tokenizer(text, token_regex=LC_REGEX)

    def parse(self) -> Term:
        term = self.parse_term()
        if self.tok.peek() is not None and self.tok.peek() != "":
            raise SyntaxError(f"Unexpected token: {self.tok.peek()}")
        return term

    def parse_term(self) -> Term:
        if self.tok.peek() == "\\":
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Term:
        self.tok.next()
        param = self.tok.next()
        if not re.match(VARIABLES_REGEX, param or ""):
            raise SyntaxError(f"Expected variable after \\, got {param}")
        dot = self.tok.next()
        if dot != ".":
            raise SyntaxError(f"Expected '.', got {dot}")
        body = self.parse_term()
        return Abs(param, body)

    def parse_app(self) -> Term:
        left = self.parse_atom()
        while True:
            nxt = self.tok.peek()
            if nxt is None or nxt in (")", "."):
                break

            if nxt == "\\":
                right = self.parse_abs()
            else:
                right = self.parse_atom()
            left = App(left, right)
        return left

    def parse_atom(self) -> Term:
        tok = self.tok.peek()
        if tok == "(":
            self.tok.next()
            term = self.parse_term()
            if self.tok.next() != ")":
                raise SyntaxError("Expected ')'")
            return term
        elif re.match(VARIABLES_REGEX, tok or ""):
            self.tok.next()
            return Var(tok)
        else:
            raise SyntaxError(f"Unexpected token: {tok}")
