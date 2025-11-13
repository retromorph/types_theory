import re

from .preprocessors import Preprocessor
from .primitives import Let, Line, Program
from src.lc.parser import LambdaParser
from src.common.tokenizer import Tokenizer


MACRO_REGEX = r"[A-Z+\-*/\[\]&|~_<>=]+"
LC_MACRO_REGEX = re.compile(rf"\s*(?:({MACRO_REGEX})|(:=)|([a-z_\\.() ]+)$)")


class LambdaLetParser:
    def __init__(self, text: str, preprocessors: list[Preprocessor]=None):
        self.text = text
        for preprocessor in preprocessors or []:
            self.text = preprocessor.perform(self.text)

        self.substitutions = {}

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
        tok = Tokenizer(line, token_regex=LC_MACRO_REGEX)
        if re.match(MACRO_REGEX, tok.peek()):
            return Line(self.parse_let(tok))
        else:
            parser = LambdaParser(line)
            return Line(parser.parse())

    def parse_let(self, tok: Tokenizer) -> Let:
        slug = tok.next()
        tok.next()
        body_str = tok.next()
        body = LambdaParser(body_str).parse()

        # hack
        if slug == 'Y' or ('Y' in self.substitutions.keys() and self.substitutions['Y'] in body_str):
            self.substitutions[slug] = body_str
            return Let(slug, body)
        else:
            reduced_body, _ = body.normalize( n_steps=1000)
            self.substitutions[slug] = repr(reduced_body)
            return Let(slug, reduced_body)
