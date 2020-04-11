def from_tokens(tokens):
    strings = []
    for token in tokens:
        strings.append(str(token))
    return ''.join(strings)


def from_ast(ast):
    strings = []
    for ast_node in ast:
        strings.append(str(ast_node))
    return ''.join(strings)
