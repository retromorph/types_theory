import os
import re
import random
import string
import pandas as pd
from src.lc.calculi_vanilla import Var, App, Abs
from abc import ABC, abstractmethod

PREPROCESSORS_DIR = 'preprocessors_tmp'


class Preprocessor(ABC):
    @abstractmethod
    def perform(self, text: str) -> str:
        pass


class NumberPreprocessor(Preprocessor):
    def __init__(self, rng: int):
        numbers_file_name = f'{PREPROCESSORS_DIR}/number_{rng}.csv'
        if os.path.exists(numbers_file_name):
            self.numbers_df = pd.read_csv(numbers_file_name)
        else:
            numbers = []
            for i in range(rng):
                numeral = self.generate_church_number(i)
                numbers.append([i, numeral.print()])
            self.numbers_df = pd.DataFrame(numbers, columns=['n', 'numeral'])
            os.makedirs(PREPROCESSORS_DIR, exist_ok=True)
            self.numbers_df.to_csv(numbers_file_name, index=False)

    def get_unique_var_name(self):
        return ''.join(random.choices(string.ascii_lowercase, k=10))

    def generate_church_number(self, n):
        # z = self.get_unique_var_name()
        # s = self.get_unique_var_name()
        z = 'z'
        s = 's'
        body = Var(z)
        for i in range(n):
            body = App(Var(s), body)
        return Abs(s, Abs(z, body))

    def perform(self, text: str) -> str:
        matches = [(m.group(), m.start(), m.end()) for m in re.finditer("[0-9]+", text)]
        offset = 0
        for match, start, end in matches:
            intron = self.numbers_df[self.numbers_df['n'] == int(match)].iloc[0]['numeral']
            text = text[:start + offset] + intron + text[end + offset:]
            offset += len(intron) - len(match)
        return text

