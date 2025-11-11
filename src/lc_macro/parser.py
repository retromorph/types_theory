import re

from .preprocessors import Preprocessor
from .primitives import Let, Line, Program
from src.lc.parser import LambdaParser
from src.lc.calculi import normalize


LET_REGEX = r"[A-Z+\-*/\[\]&|~_<>=]+"
VARIABLES_REGEX = r"[a-z_]+"
TOKEN_REGEX = re.compile(r"\s*(?:([A-Z+\-*/\[\]&|~_<>=]+)|(:=)|([a-z_\\.() ]+)$)")


class LambdaLetTokenizer:
    def __init__(self, text: str):
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


class LambdaLetParser:
    def __init__(self, text: str, preprocessors: list[Preprocessor]=None):
        self.text = text
        for preprocessor in preprocessors or []:
            self.text = preprocessor.perform(self.text)

        self.substitutions = {}

    # def perform_substitution(self, line: str) -> str:
    #     if len(self.substitutions) == 0:
    #         return line
    #     pattern = re.compile("|".join(re.escape(k) for k in self.substitutions.keys()))
    #     return pattern.sub(lambda m: f"({self.substitutions[m.group(0)]})", line)

    def perform_substitution(self, line: str) -> str:
        if len(self.substitutions) == 0:
            return line
        # Custom "word boundary" — negative lookbehind and lookahead
        # Matches if NOT preceded/followed by allowed word characters.
        pattern = r'(?<![A-Z+\-*/\[\]&|~_<>=])({})(?![A-Z+\-*/\[\]&|~_<>=])'.format(
            "|".join(re.escape(k) for k in self.substitutions.keys())
        )

        def repl(match: re.Match):
            return f"({self.substitutions[match.group(1)]})"

        return re.sub(pattern, repl, line)

    def parse(self) -> Program:
        lines = self.text.replace('\n', ' ').split(";")
        program = Program()
        for line in lines:
            program.lines.append(self.parse_line(line))
        return program

    def parse_line(self, line: str) -> Line:
        line = self.perform_substitution(line)
        tok = LambdaLetTokenizer(line)
        if re.match(LET_REGEX, tok.peek()):
            return Line(self.parse_let(tok))
        else:
            parser = LambdaParser(line)
            return Line(parser.parse())

    def parse_let(self, tok: LambdaLetTokenizer) -> Let:
        # slug = tok.next()
        # tok.next()
        # body_str = tok.next()
        # if slug == "<":
        #     print(slug)
        #     print(body_str)
        #     # print(reduced_body.print())
        #     print('=============')
        # body = LambdaParser(body_str).parse()
        # self.substitutions[slug] = body_str
        # return Let(slug, body)
        slug = tok.next()
        tok.next()
        body_str = tok.next()
        body = LambdaParser(body_str).parse()

        # hack
        if slug == 'Y' or ('Y' in self.substitutions.keys() and self.substitutions['Y'] in body_str):
            self.substitutions[slug] = body_str
            return Let(slug, body)
        else:
            reduced_body = normalize(body, n_steps=1000, trace=False)
            self.substitutions[slug] = reduced_body.print()
            return Let(slug, reduced_body)

    def execute(self):
        program = self.parse()

        pass