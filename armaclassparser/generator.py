def from_tokens(tokens):
    for token in tokens:
        print(str(token), end='')


def from_ast(ast):
    for ast_node in ast:
        print(str(ast_node), end='')
