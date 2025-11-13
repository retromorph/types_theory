import sys
from pprint import pprint

from src.common.benchmark import benchmark
from src.lc.calculi_vanilla import Term
from .parser import LambdaParser


class CLI:
    def __init__(self, variables: dict[str, str]):
        self.variables = variables
        self.trace = variables.get('trace', 'None')

    def run(self):
        if 'I' in self.variables:
            self.run_from_file()
        else:
            self.run_from_stdin()

    def run_from_file(self):
        with open(self.variables['I'], "r", encoding="utf-8") as input_file:
            program = input_file.read()
            lambda_parser = LambdaParser(program)
            parsed_term = lambda_parser.parse()
            normalized_term = self.normalize(parsed_term)

            if 'O' in self.variables:
                with open(self.variables['O'], "w", encoding="utf-8") as output_file:
                    output_file.write(str(normalized_term))
            else:
                print(normalized_term)

    def run_from_stdin(self):
        while True:
            try:
                program = input('> ')
                lambda_parser = LambdaParser(program)
                parsed_term = lambda_parser.parse()

                print(self.normalize(parsed_term))
            except SyntaxError as err:
                print(err)
                break

    def normalize(self, term: Term) -> Term:
        if self.trace == 'None':
            normalized_term, _ = term.normalize()
            return normalized_term

        if self.trace == 'Low':
            stats = benchmark(term.normalize, measure_time=True)
        elif self.trace == 'Mid':
            stats = benchmark(term.normalize, measure_time=True, measure_tracemalloc=True, measure_profile=False, measure_allocs=True)
        else:
            stats = benchmark(term.normalize, measure_time=True, measure_tracemalloc=True, measure_profile=True, measure_allocs=True)

        normalized_term, n_steps = stats['result']
        del stats['result']
        stats['steps'] = n_steps
        print("================================================")
        pprint(stats)
        print("================================================")
        return normalized_term

if __name__ == '__main__':
    variables = dict(map(lambda x: x.replace('-', '').split('='), sys.argv[1:]))

    cli = CLI(variables)
    cli.run()
