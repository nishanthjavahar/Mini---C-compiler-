from lexer.lexer import tokenize
from parser.parser import Parser
from semantic.semantic import SemanticAnalyzer
from ir.tac import TACGenerator
from utils.printer import print_results
from utils.ast_visualizer import print_ast
import sys
from ir.optimizer import ConstantFolder


def compile_minic(source):

    result = {
        'tokens': [],
        'symbol_table': [],
        'tac': [],
        'errors': [],
    }

    # Stage 1
    tokens, lex_errors = tokenize(source)

    result['errors'].extend(lex_errors)

    result['tokens'] = [
        {
            'type': t.type,
            'value': t.value,
            'line': t.line
        }
        for t in tokens
    ]

    # Stage 2
    parser = Parser(tokens)

    ast = parser.parse_program()
    optimizer = ConstantFolder()

    ast = optimizer.fold(ast)   
    print("\n" + "=" * 60)
    print("AST VISUALIZATION")
    print("=" * 60)

    print_ast(ast)

    result['errors'].extend(parser.errors)

    # Stage 3
    sem = SemanticAnalyzer()

    sem.analyze(ast)

    result['errors'].extend(sem.errors)

    result['symbol_table'] = sem.sym_table.to_table()

    # Stage 4
    tac_gen = TACGenerator()

    tac_gen.gen(ast)

    result['tac'] = tac_gen.code

    return result


if __name__ == '__main__':

    if len(sys.argv) < 2:

        print("Usage: python3 main.py tests/test_program.mc")

        sys.exit(1)

    filename = sys.argv[1]

    try:

        with open(filename, 'r') as f:

            source_code = f.read()

    except FileNotFoundError:

        print(f"Error: File '{filename}' not found.")

        sys.exit(1)

    print(f"\\nCompiling: {filename}\\n")

    output = compile_minic(source_code)

    print_results(output)