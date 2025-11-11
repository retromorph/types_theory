import re
from .primitives import Term, Var, App, Abs


VARIABLES_REGEX = r"[a-z_][a-z_]*"
TOKEN_REGEX = re.compile(r"\s*(?:(\\)|(\.)|(\()|(\))|([a-z_][a-z_]*)|$)")


class LambdaTokenizer:
    def __init__(self, text):
        self.tokens = TOKEN_REGEX.findall(text)
        self.index = 0

    def peek(self):
        if self.index >= len(self.tokens):
            return None
        for group in self.tokens[self.index]:
            if group:
                return group
        return None

    def next(self):
        tok = self.peek()
        self.index += 1
        return tok


class LambdaParser:
    def __init__(self, text):
        self.tok = LambdaTokenizer(text)

    def parse(self) -> Term:
        term = self.parse_term()
        if self.tok.peek() is not None and self.tok.peek() != '':
            raise SyntaxError(f"Unexpected token: {self.tok.peek()}")
        return term

    def parse_term(self) -> Term:
        if self.tok.peek() == '\\':
            return self.parse_abs()
        else:
            return self.parse_app()

    def parse_abs(self) -> Term:
        self.tok.next()
        param = self.tok.next()
        if not re.match(VARIABLES_REGEX, param or ""):
            raise SyntaxError(f"Expected variable after \\, got {param}")
        dot = self.tok.next()
        if dot != '.':
            raise SyntaxError(f"Expected '.', got {dot}")
        body = self.parse_term()
        return Abs(param, body)

    def parse_app(self) -> Term:
        left = self.parse_atom()
        while True:
            nxt = self.tok.peek()
            if nxt is None or nxt in (')', '.'):
                break

            if nxt == '\\':
                right = self.parse_abs()
            else:
                right = self.parse_atom()
            left = App(left, right)
        return left

    def parse_atom(self) -> Term:
        tok = self.tok.peek()
        if tok == '(':
            self.tok.next()
            term = self.parse_term()
            if self.tok.next() != ')':
                raise SyntaxError("Expected ')'")
            return term
        elif re.match(VARIABLES_REGEX, tok or ""):
            self.tok.next()
            return Var(tok)
        else:
            raise SyntaxError(f"Unexpected token: {tok}")
