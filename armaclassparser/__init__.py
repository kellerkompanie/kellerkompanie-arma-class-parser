from armaclassparser import generator
from armaclassparser.lexer import Lexer


def parse_file(file_path: str):
    with open(file_path, 'r') as fp:
        input_data = fp.read()
    return parse_string(input_data)


def parse_string(input_data: str):
    tokens = Lexer(input_data).tokenize()
    return tokens
