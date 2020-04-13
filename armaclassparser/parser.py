import sys
from parser import ParserError
from typing import Union

import armaclassparser
from armaclassparser.ast import StringLiteral, Constant, Identifier, ArrayDeclaration, Assignment, ClassDefinition, \
    Array
from armaclassparser.lexer import TokenType, Token


class TokenProcessor:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def token(self) -> Token:
        return self.tokens[self.index]

    def next(self) -> Token:
        self.index += 1
        return self.token()

    def has_next(self) -> bool:
        return self.index < len(self.tokens) - 1

    def last(self) -> Token:
        if self.index <= 0:
            raise ValueError('invalid index: {}', self.index)
        return self.tokens[self.index - 1]

    def expect(self, token_type: Union[TokenType, list]) -> Token:
        if isinstance(token_type, TokenType):
            if self.token().token_type != token_type:
                raise armaclassparser.UnexpectedTokenError(token_type, self.token())
        elif isinstance(token_type, list):
            if self.token().token_type not in token_type:
                raise armaclassparser.UnexpectedTokenError(token_type, self.token())
        return self.token()

    def expect_next(self, token_type: Union[TokenType, list]) -> Token:
        self.next()
        self.expect(token_type)
        return self.token()

    def skip_whitespaces(self, include_newlines=False):
        skip_tokens = [TokenType.WHITESPACE, TokenType.TAB] + ([TokenType.NEWLINE] if include_newlines else [])
        while self.token().token_type in skip_tokens and self.index < len(self.tokens):
            self.next()


class Parser(TokenProcessor):
    def __init__(self, tokens):
        TokenProcessor.__init__(self, tokens)
        self.stack = []

    def _parse_string_literal(self):
        tokens = [self.token()]

        if tokens[0].token_type not in [TokenType.DOUBLE_QUOTES, TokenType.QUOTE]:
            raise armaclassparser.UnexpectedTokenError([TokenType.DOUBLE_QUOTES, TokenType.QUOTE], tokens[0])

        self.index += 1
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.token_type == tokens[0].token_type:
                tokens.append(token)
                self.index += 1
                return StringLiteral(tokens)
            else:
                tokens.append(token)
                self.index += 1

        raise armaclassparser.MissingTokenError(tokens[0].token_type)

    def _parse_constant(self):
        number_literal_token = self.expect(TokenType.NUMBER)
        self.next()
        return Constant(number_literal_token)

    def _parse_identifier(self):
        name_token = self.expect(TokenType.WORD)
        self.index += 1
        return Identifier(name_token)

    def _parse_array_declaration(self):
        l_square = self.expect(TokenType.L_SQUARE)
        r_square = self.expect_next(TokenType.R_SQUARE)
        self.index += 1

        identifier = self.stack.pop()
        if not isinstance(identifier, Identifier):
            raise ParserError('expected identifier for array declaration, but got {}'.format(repr(identifier)))

        return ArrayDeclaration(identifier, l_square, r_square)

    def _parse_assignment(self):
        equals_token = self.expect(TokenType.EQUALS)
        self.next()

        left_side = self.stack.pop()
        if not isinstance(left_side, Identifier) and not isinstance(left_side, ArrayDeclaration):
            raise ParserError(
                'unexpected left side of assignment, expected Identifier or ArrayDeclaration, but got {}'.format(
                    repr(left_side)))

        self.skip_whitespaces()
        token = self.token()

        if token.token_type == TokenType.WORD:
            right_side = self._parse_identifier()
        elif token.token_type in [TokenType.QUOTE, TokenType.DOUBLE_QUOTES]:
            right_side = self._parse_string_literal()
        elif token.token_type == TokenType.NUMBER:
            right_side = self._parse_constant()
        elif token.token_type == TokenType.L_CURLY:
            right_side = self._parse_array()
        else:
            raise armaclassparser.ParsingError('unexpected right side of assignment: {}'.format(token))

        semicolon_token = self.expect(TokenType.SEMICOLON)
        self.index += 1
        return Assignment(left_side, equals_token, right_side, semicolon_token)

    def _parse_array(self):
        l_curly_token = self.expect(TokenType.L_CURLY)
        token = self.next()

        children = []
        while token.token_type != TokenType.R_CURLY and self.index < len(self.tokens):
            if token.token_type in [TokenType.WHITESPACE, TokenType.TAB, TokenType.NEWLINE]:
                self.skip_whitespaces(include_newlines=True)
            token = self.token()

            if token.token_type == TokenType.NUMBER:
                children.append(self._parse_constant())
            elif token.token_type in [TokenType.QUOTE, TokenType.DOUBLE_QUOTES]:
                children.append(self._parse_string_literal())
            elif token.token_type == TokenType.WORD:
                children.append(self._parse_identifier())
            elif token.token_type == TokenType.L_CURLY:
                children.append(self._parse_array())
            else:
                raise ParserError('encountered unexpected token while parsing array: {}'.format(repr(token)))

            self.skip_whitespaces(include_newlines=True)
            self.expect([TokenType.COMMA, TokenType.R_CURLY])
            if self.token().token_type == TokenType.COMMA:
                token = self.next()
                continue
            else:
                break

        r_curly_token = self.expect(TokenType.R_CURLY)
        self.index += 1
        return Array(l_curly_token, children, r_curly_token)

    def _parse_class_definition(self):
        class_keyword_token = self.expect(TokenType.KEYWORD_CLASS)
        self.next()
        self.skip_whitespaces()

        class_name_token = self.expect(TokenType.WORD)
        self.next()
        self.skip_whitespaces()

        token = self.token()
        parent_class_token = None
        if token.token_type == TokenType.COLON:
            self.next()
            self.skip_whitespaces()
            parent_class_token = self.token()
            self.next()
            self.skip_whitespaces()

        if self.token().token_type == TokenType.L_CURLY:
            l_curly_token = self.token()
            self.next()

            previous_stack = self.stack
            self.stack = []
            while self.token().token_type != TokenType.R_CURLY and self.index < len(self.tokens):
                child = self._parse_next()
                if child is not None:
                    self.stack.append(child)

            body = self.stack
            self.stack = previous_stack

            if self.token().token_type == TokenType.R_CURLY:
                colon_token = self.next()
                if colon_token.token_type != TokenType.SEMICOLON:
                    raise armaclassparser.UnexpectedTokenError(TokenType.SEMICOLON, colon_token)
                self.index += 1
                return ClassDefinition(class_keyword_token, class_name_token, body, parent_class_token)
            else:
                raise armaclassparser.MissingTokenError(TokenType.R_CURLY, l_curly_token)
        else:
            raise armaclassparser.UnexpectedTokenError(TokenType.L_CURLY, self.token())

    def _parse_next(self):
        token = self.token()
        if token.token_type in [TokenType.DOUBLE_QUOTES, TokenType.QUOTE]:
            return self._parse_string_literal()
        elif token.token_type == TokenType.KEYWORD_CLASS:
            return self._parse_class_definition()
        elif token.token_type in [TokenType.NEWLINE, TokenType.TAB]:
            self.index += 1
            return None
        elif token.token_type == TokenType.WORD:
            return self._parse_identifier()
        elif token.token_type == TokenType.L_SQUARE:
            return self._parse_array_declaration()
        elif token.token_type == TokenType.L_CURLY:
            return self._parse_array()
        elif token.token_type == TokenType.EQUALS:
            return self._parse_assignment()
        elif token.token_type in [TokenType.WHITESPACE, TokenType.TAB, TokenType.NEWLINE]:
            self.index += 1
            return None
        elif token.token_type == TokenType.KEYWORD_INCLUDE:
            raise armaclassparser.ParsingError('expected includes to be handled by preprocessor')
        elif token.token_type in [TokenType.COMMENT, TokenType.MCOMMENT_START, TokenType.MCOMMENT_END]:
            raise armaclassparser.ParsingError('expected comments to be handled by preprocessor')
        else:
            print('WARNING: unknown token:', repr(token), file=sys.stderr)
            self.index += 1
            return None

    def parse(self):
        while self.index < len(self.tokens):
            ast_node = self._parse_next()
            if ast_node is not None:
                self.stack.append(ast_node)

        return self.stack
