from enum import Enum

from armaclassparser.lexer import Token, TokenType


class ASTNodeType(Enum):
    STRING_LITERAL = 'STRING_LITERAL'
    IDENTIFIER = 'IDENTIFIER'
    CONSTANT = 'CONSTANT'
    ARRAY = 'ARRAY'
    ARRAY_DECLARATION = 'ARRAY_DECLARATION'
    INCLUDE_STATEMENT = 'INCLUDE_STATEMENT'
    CLASS_DEFINITION = 'CLASS_DEFINITION'


class ASTNode:
    def __init__(self, node_type: ASTNodeType, tokens: list, line_no: int, line_pos: int):
        if not node_type:
            raise TypeError('parameter node_type cannot be None')
        if not tokens:
            raise TypeError('parameter tokens cannot be None')
        if not line_no:
            raise TypeError('parameter line_no cannot be None')
        if not line_pos:
            raise TypeError('parameter line_pos cannot be None')
        if len(tokens) == 0:
            raise ValueError('parameter tokens cannot be empty')
        if line_no <= 0:
            raise ValueError('parameter line_no must be greater than 0')
        if line_pos <= 0:
            raise ValueError('parameter line_pos must be greater than 0')

        self.type = node_type
        self.tokens = tokens
        self.line_no = line_no
        self.line_pos = line_pos

    def __eq__(self, other):
        if isinstance(other, ASTNode):
            return self.type == other.type \
                   and self.tokens == other.tokens \
                   and self.line_no == other.line_no \
                   and self.line_pos == other.line_pos
        else:
            return False


class StringLiteral(ASTNode):
    def __init__(self, tokens: list):
        ASTNode.__init__(self, ASTNodeType.STRING_LITERAL, tokens, tokens[0].line_no, tokens[0].line_pos)
        self.value = ''.join(token.value for token in tokens[1:-1])

    def __str__(self):
        return '"{}"'.format(self.value)


class Constant(ASTNode):
    def __init__(self, number_token: Token):
        if not number_token:
            raise TypeError('parameter number_token cannot be None')
        if number_token.token_type != TokenType.NUMBER_LITERAL:
            raise ValueError('parameter number_token must be of type {}'.format(TokenType.NUMBER_LITERAL))

        ASTNode.__init__(self, ASTNodeType.CONSTANT, [number_token], number_token.line_no, number_token.line_pos)
        self.value = float(number_token.value) if '.' in number_token.value else int(number_token.value)

    def __str__(self):
        return str(self.value)


class Identifier(ASTNode):
    def __init__(self, name_token: Token):
        if not name_token:
            raise TypeError('parameter name_token cannot be None')
        if name_token.token_type != TokenType.STRING_LITERAL:
            raise ValueError('parameter name_token must be of type {}'.format(TokenType.STRING_LITERAL))

        ASTNode.__init__(self, ASTNodeType.IDENTIFIER, [name_token], name_token.line_no, name_token.line_pos)
        self.name_token = name_token
        self.value = name_token.value

    def __str__(self):
        return '"{}"'.format(self.value)


class ArrayDeclaration(ASTNode):
    def __init__(self, identifier: Identifier, left_bracket_token: Token, right_bracket_token: Token):
        if not identifier:
            raise TypeError('parameter identifier cannot be None')
        if not left_bracket_token:
            raise TypeError('parameter left_bracket_token cannot be None')
        if not left_bracket_token:
            raise TypeError('parameter right_bracket_token cannot be None')
        if left_bracket_token.token_type != TokenType.L_SQUARE:
            raise ValueError('parameter left_bracket_token must be of type {}'.format(TokenType.L_SQUARE))
        if right_bracket_token.token_type != TokenType.R_SQUARE:
            raise ValueError('parameter right_bracket_token must be of type {}'.format(TokenType.R_SQUARE))

        ASTNode.__init__(self, ASTNodeType.ARRAY_DECLARATION,
                         identifier.tokens + [left_bracket_token, right_bracket_token], identifier.line_no,
                         identifier.line_pos)
        self.identifier = identifier

    def __str__(self):
        return '"{}"'.format(self.identifier.value)


class Array(ASTNode):
    def __init__(self, left_curly_token: Token, children: list, right_curly_token: Token):
        if not left_curly_token:
            raise TypeError('parameter left_curly_token cannot be None')
        if not children:
            raise TypeError('parameter children cannot be None')
        if not right_curly_token:
            raise TypeError('parameter right_curly_token cannot be None')
        if left_curly_token.token_type != TokenType.L_CURLY:
            raise ValueError('parameter left_curly_token must be of type {}'.format(TokenType.L_CURLY))
        if right_curly_token.token_type != TokenType.R_CURLY:
            raise ValueError('parameter right_curly_token must be of type {}'.format(TokenType.R_CURLY))

        ASTNode.__init__(self, ASTNodeType.ARRAY, [left_curly_token, right_curly_token], left_curly_token.line_no,
                         left_curly_token.line_pos)
        self.children = children

    def __str__(self):
        strings = ["{"]
        child_strings = []
        for child in self.children:
            child_strings.append(str(child))
        strings.append(','.join(child_strings))
        strings.append("}")
        return ''.join(strings)


class Assignment(ASTNode):
    def __init__(self, left: ASTNode, equals_token: Token, right: ASTNode, semicolon_token: Token):
        if not left:
            raise TypeError('parameter left cannot be None')
        if not equals_token:
            raise TypeError('parameter equals_token cannot be None')
        if not right:
            raise TypeError('parameter right cannot be None')
        if not semicolon_token:
            raise TypeError('parameter semicolon_token cannot be None')
        if equals_token.token_type != TokenType.EQUALS:
            raise ValueError('parameter equals_token must be of type {}'.format(TokenType.EQUALS))
        if semicolon_token.token_type != TokenType.SEMICOLON:
            raise ValueError('parameter semicolon_token must be of type {}'.format(TokenType.SEMICOLON))

        ASTNode.__init__(self, ASTNodeType.ARRAY_DECLARATION,
                         left.tokens + [equals_token] + right.tokens + [semicolon_token],
                         equals_token.line_no,
                         equals_token.line_pos)
        self.left = left
        self.right = right

    def __str__(self):
        return '{} = {};'.format(self.left, self.right)


class IncludeStatement(ASTNode):
    def __init__(self, include_token: Token, string_literal: StringLiteral):
        ASTNode.__init__(self, ASTNodeType.INCLUDE_STATEMENT, [include_token] + string_literal.tokens,
                         include_token.line_no, include_token.line_pos)
        self.value = string_literal.value

    def __str__(self):
        return '#include "{}"'.format(self.value)


class ClassDefinition(ASTNode):
    def __init__(self, class_keyword_token: Token, class_name_token: Token, body, parent_class_token: Token):
        tokens = [class_keyword_token, class_name_token] + ([parent_class_token] if parent_class_token else [])
        ASTNode.__init__(self, ASTNodeType.CLASS_DEFINITION, tokens, class_keyword_token.line_no,
                         class_keyword_token.line_pos)
        self.class_name = class_name_token.value
        self.parent_class = parent_class_token.value if parent_class_token else None
        self.body = body

    def __str__(self):
        strings = ["class " + self.class_name]
        strings += [self.parent_class.value] if self.parent_class else []
        strings += [" {\n", str(self.body), "\n};"]
        return ''.join(strings)
