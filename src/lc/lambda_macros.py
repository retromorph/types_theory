from .lambda_semantics import ChurchNumeralMacros, PlusMacros, MultiplyMacros, SubstractionMacros, TrueMacros, FalseMacros, CombinatorMacros


class MacrosParser:
    def __init__(self, text):
        self.text = text
        self.macros = [
            ChurchNumeralMacros(),
            PlusMacros(),
            MultiplyMacros(),
            TrueMacros(),
            FalseMacros(),
            CombinatorMacros(),
            SubstractionMacros(),
        ]

    def parse(self) -> str:
        for macro in self.macros:
            self.text = macro.perform(self.text)
        return self.text
