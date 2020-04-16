from armaclassparser import generator, lexer, parser, preprocessor


def parse_from_file(file_path: str, pre_process=True):
    with open(file_path, 'r', encoding='utf-8', newline=None) as fp:
        input_data = fp.read()

    tokens = lexer.Lexer(input_data, file_path).tokenize()

    if pre_process:
        pre_processor = preprocessor.PreProcessor(tokens, file_path)
        tokens = pre_processor.preprocess()

    p = parser.Parser(tokens)
    ast = p.parse()

    return ast


def parse_from_string(input_data: str, pre_process=True):
    tokens = lexer.Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()

    if pre_process:
        pre_processor = preprocessor.PreProcessor(tokens, lexer.STRING_INPUT_FILE)
        tokens = pre_processor.preprocess()

    p = parser.Parser(tokens)
    ast = p.parse()

    return ast
