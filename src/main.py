import re
import cProfile

from src.lc.calculi_optimized import Term
from src.lc.calculi_lazy import Term as TermLazy
from lc_macro.parser import LambdaLetParser
from src.lc_macro.preprocessors import NumberPreprocessor


def church_to_int(expr: str) -> int:
    # Normalize expression (replace λ with backslash, remove extra spaces)
    expr = expr.replace('λ', '\\').strip()

    # Basic pattern: \s.\z.<body>
    # It accepts any variable names, not necessarily 's' and 'z'
    m = re.match(r"^\\([a-zA-Z_][a-zA-Z0-9_]*)\.\s*\\([a-zA-Z_][a-zA-Z0-9_]*)\.(.*)$", expr)
    if not m:
        raise ValueError("Invalid Church numeral structure")

    s_var, z_var, body = m.groups()

    # Strip outer parentheses and spaces
    body = body.strip()

    # Count how many times `s_var` is applied to `z_var`
    # We expect something like: s (s (s z)) or s(s(s(s z)))
    # Step-by-step parsing of nested applications
    count = 0
    while True:
        # Remove outer parentheses around single expression
        body = body.strip()
        # If body == z_var -> stop
        if body == z_var:
            return count
        # If it starts with s_var
        if body.startswith(s_var):
            count += 1
            # remove leading s_var and optional space/parenthesis
            body = body[len(s_var):].strip()
            if body.startswith('(') and body.endswith(')'):
                body = body[1:-1].strip()
            continue
        # Sometimes structure is s (s (...)) or s(s(...))
        m = re.match(rf"^{s_var}\s*\((.*)\)$", body)
        if m:
            count += 1
            body = m.group(1)
            continue
        raise ValueError(f"Unexpected structure after {count} applications: {body!r}")


# program = input()
# lambda_parser = LambdaParser(program)
# parsed_term = lambda_parser.parse()
# print(parsed_term.print())
# print(normalize(parsed_term).print())
# print("\n\n\n\n\n\n")


with open("src/program.lc", "r", encoding="utf-8") as file:
    program = file.read()

    lambda_let_parser = LambdaLetParser(program, preprocessors=[NumberPreprocessor(rng=100)])
    parsed_program = lambda_let_parser.parse()

    # print(parsed_program.lines[-1].print(pretty=True))
    # print("=======================")

    for line in parsed_program.lines:
        if isinstance(line.value, TermLazy):
            print(repr(line.value))
            # result = cProfile.run('normalize(line.value, trace=True)')
            result, _ = line.value.normalize()
            print(f"Steps: {_}")
            try:
                print(church_to_int(str(result)))
            except:
                print(result)
            print("=======================")

# \x. \y. \s. \z. x s (y s z)
# + := \x. \y. \s. \z. x s (y s z);
# + 1 2