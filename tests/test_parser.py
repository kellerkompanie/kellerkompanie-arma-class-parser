import os
import unittest

from armaclassparser import lexer
from armaclassparser.ast import Array
from armaclassparser.lexer import Lexer, Token, TokenType
from armaclassparser.parser import Parser, Identifier, Constant, Assignment, StringLiteral, ArrayDeclaration


class TestParser(unittest.TestCase):

    def test_identifier1(self):
        input_data = "x"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(1, len(tokens))

        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        expected_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value="x")
        identifier = Identifier(expected_token)
        self.assertEqual([identifier], ast)

    def test_identifier2(self):
        input_data = "CfgPatches"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(1, len(tokens))

        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        expected_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value="CfgPatches")
        identifier = Identifier(expected_token)
        self.assertEqual([identifier], ast)

    def test_identifier3(self):
        input_data = "class0"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(1, len(tokens))

        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        expected_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value="class0")
        identifier = Identifier(expected_token)
        self.assertEqual([identifier], ast)

    def test_assignment1(self):
        input_data = "a = 1337;"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        left_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='a')
        equals_token = Token(TokenType.EQUALS, lexer.STRING_INPUT_FILE, 1, 3)
        right_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 5, value='1337')
        semicolon_token = Token(TokenType.SEMICOLON, lexer.STRING_INPUT_FILE, 1, 9)

        left_ast = Identifier(left_token)
        right_ast = Constant(right_token)

        assignment = Assignment(left_ast, equals_token, right_ast, semicolon_token)
        self.assertEqual([assignment], ast)

    def test_assignment2(self):
        input_data = "a=1337;"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        left_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='a')
        equals_token = Token(TokenType.EQUALS, lexer.STRING_INPUT_FILE, 1, 2)
        right_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 3, value='1337')
        semicolon_token = Token(TokenType.SEMICOLON, lexer.STRING_INPUT_FILE, 1, 7)

        left_ast = Identifier(left_token)
        right_ast = Constant(right_token)

        assignment = Assignment(left_ast, equals_token, right_ast, semicolon_token)
        self.assertEqual([assignment], ast)

    def test_assignment3(self):
        input_data = "a = 'Hello';"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        left_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='a')
        equals_token = Token(TokenType.EQUALS, lexer.STRING_INPUT_FILE, 1, 3)
        right_tokens = [
            Token(TokenType.QUOTE, lexer.STRING_INPUT_FILE, 1, 5),
            Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 6, value='Hello'),
            Token(TokenType.QUOTE, lexer.STRING_INPUT_FILE, 1, 11)
        ]
        semicolon_token = Token(TokenType.SEMICOLON, lexer.STRING_INPUT_FILE, 1, 12)

        left_ast = Identifier(left_token)
        right_ast = StringLiteral(right_tokens)

        assignment = Assignment(left_ast, equals_token, right_ast, semicolon_token)
        self.assertEqual([assignment], ast)

    def test_assignment4(self):
        input_data = 'author = "Schwaggot";'
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        left_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='author')
        equals_token = Token(TokenType.EQUALS, lexer.STRING_INPUT_FILE, 1, 8)
        right_tokens = [
            Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 10),
            Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 11, value='Schwaggot'),
            Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 20)
        ]
        semicolon_token = Token(TokenType.SEMICOLON, lexer.STRING_INPUT_FILE, 1, 21)

        left_ast = Identifier(left_token)
        right_ast = StringLiteral(right_tokens)

        assignment = Assignment(left_ast, equals_token, right_ast, semicolon_token)
        self.assertEqual([assignment], ast)

    def test_array_declaration1(self):
        input_data = "array[]"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        name = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='array')
        l_square_token = Token(TokenType.L_SQUARE, lexer.STRING_INPUT_FILE, 1, 6)
        r_square_token = Token(TokenType.R_SQUARE, lexer.STRING_INPUT_FILE, 1, 7)

        identifier = Identifier(name)
        array_declaration = ArrayDeclaration(identifier, l_square_token, r_square_token)

        self.assertEqual([array_declaration], ast)

    def test_array_empty(self):
        input_data = "{}"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 2)

        array = Array(l_curly_token, [], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_simple1(self):
        input_data = "{1}"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 2, value='2')
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 3)

        constant = Constant(number_token)
        array = Array(l_curly_token, [constant], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_simple2(self):
        input_data = "{ 1 }"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 3, value='2')
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 5)

        constant = Constant(number_token)
        array = Array(l_curly_token, [constant], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_simple3(self):
        input_data = "{1,2,3}"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token1 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 2, value='1')
        number_token2 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 4, value='2')
        number_token3 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 6, value='3')
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 7)

        constant1 = Constant(number_token1)
        constant2 = Constant(number_token2)
        constant3 = Constant(number_token3)
        array = Array(l_curly_token, [constant1, constant2, constant3], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_simple4(self):
        input_data = "{1, 2,3}"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token1 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 2, value='1')
        number_token2 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 5, value='2')
        number_token3 = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 7, value='3')
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 8)

        constant1 = Constant(number_token1)
        constant2 = Constant(number_token2)
        constant3 = Constant(number_token3)
        array = Array(l_curly_token, [constant1, constant2, constant3], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_simple5(self):
        input_data = "array[] = {};"
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        name = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 1, value='array')
        l_square_token = Token(TokenType.L_SQUARE, lexer.STRING_INPUT_FILE, 1, 6)
        r_square_token = Token(TokenType.R_SQUARE, lexer.STRING_INPUT_FILE, 1, 7)
        identifier = Identifier(name)
        array_declaration = ArrayDeclaration(identifier, l_square_token, r_square_token)

        equals_token = Token(TokenType.EQUALS, lexer.STRING_INPUT_FILE, 1, 9)

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 11)
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 12)
        array = Array(l_curly_token, [], r_curly_token)

        semicolon_token = Token(TokenType.SEMICOLON, lexer.STRING_INPUT_FILE, 1, 13)

        assignment = Assignment(array_declaration, equals_token, array, semicolon_token)

        self.assertEqual([assignment], ast)

    def test_array_mixed1(self):
        input_data = '{1, "hello"}'
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 2, value='1')
        l_double_quotes_token = Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 5)
        string_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 6, value='hello')
        r_double_quotes_token = Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 11)
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 12)

        constant = Constant(number_token)
        string_literal = StringLiteral([l_double_quotes_token, string_token, r_double_quotes_token])
        array = Array(l_curly_token, [constant, string_literal], r_curly_token)

        self.assertEqual([array], ast)

    def test_array_mixed2(self):
        input_data = '{1, "hello", {}}'
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        ast = parser.parse()
        self.assertEqual(1, len(ast))

        l_curly_token = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 1)
        number_token = Token(TokenType.NUMBER, lexer.STRING_INPUT_FILE, 1, 2, value='1')
        l_double_quotes_token = Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 5)
        string_token = Token(TokenType.WORD, lexer.STRING_INPUT_FILE, 1, 6, value='hello')
        r_double_quotes_token = Token(TokenType.DOUBLE_QUOTES, lexer.STRING_INPUT_FILE, 1, 11)
        l_curly_token_inner = Token(TokenType.L_CURLY, lexer.STRING_INPUT_FILE, 1, 14)
        r_curly_token_inner = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 15)
        r_curly_token = Token(TokenType.R_CURLY, lexer.STRING_INPUT_FILE, 1, 16)

        constant = Constant(number_token)
        string_literal = StringLiteral([l_double_quotes_token, string_token, r_double_quotes_token])
        empty_array = Array(l_curly_token_inner, [], r_curly_token_inner)
        array = Array(l_curly_token, [constant, string_literal, empty_array], r_curly_token)

        self.assertEqual([array], ast)

    def test_file_sample01(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "examples/01_simple_config.cpp")
        with open(file_path, 'r') as fp:
            input_data = fp.read()
        tokens = Lexer(input_data, file_path).tokenize()
        parser = Parser(tokens, lexer.STRING_INPUT_FILE)
        parser.parse()
