import re
from .primitives import Term, Var, App, Abs
from .parser import LambdaParser


class ChurchNumeralMacros:
    pattern = r"[0-9]+"

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand(int(match)).print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self, i0: int) -> Term:
        body = Var('z')
        for i in range(i0):
            body = App(Var('s'), body)
        return Abs('s', Abs('z', body))

    def church_to_int(text: str) -> int:
        text = text.replace(" ", "")
        m = re.match(r"\\(\w+)\.\\(\w+)\.(.*)", text)
        if not m:
            raise ValueError("Not a valid Church numeral")
        s, z, body = m.groups()
        count = 0
        while body.startswith(f"{s}("):
            body = body[len(s)+1:-1]
            count += 1
        if body != z:
            raise ValueError(f"Unexpected tail: {body}")
        return count


class PlusMacros:
    pattern = r'\+'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\x. \\y. \\s. \\z. x s (y s z)").parse()


class SubstractionMacros:
    pattern = r'\-'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\m. \\n. n(\\n. \\f. \\x. n(\\g. \\h. h (g f))(\\u. x)(\\u. u)) m").parse()



class MultiplyMacros:
    pattern = r'\*'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\x. \\y. \\s. x (y s)").parse()


class TrueMacros:
    pattern = r'TRUE'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\x. \\y. x").parse()


class FalseMacros:
    pattern = r'FALSE'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\x. \\y. y").parse()


class CombinatorMacros:
    pattern = r'Y'

    def perform(self, text: str):
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer(self.pattern, text)]
        offset = 0
        for match, start, end in matches:
            intron = self.expand().print()
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

    def expand(self) -> Term:
        return LambdaParser("\\f.(\\x.f (x x)) \\x.f (x x)").parse()


