class Tokenizer:
    def __init__(self, text: str, token_regex):
        self.tokens = token_regex.findall(text)
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
