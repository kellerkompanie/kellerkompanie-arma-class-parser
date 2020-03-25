import unittest

from armaclassparser.lexer import Token, Symbol, Keyword, Literal, Lexer


class TestLexer(unittest.TestCase):

    def test_class_simple(self):
        input_data = 'class'
        expected = [
            Token(Keyword.CLASS, 1, 1)
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_class(self):
        input_data = 'class Foo {};'
        expected = [
            Token(Keyword.CLASS, 1, 1),
            Token(Symbol.WHITESPACE, 1, 6),
            Token(Literal.STRING_LITERAL, 1, 7, 'Foo'),
            Token(Symbol.WHITESPACE, 1, 10),
            Token(Symbol.L_CURLY, 1, 11),
            Token(Symbol.R_CURLY, 1, 12),
            Token(Symbol.SEMICOLON, 1, 13)
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_include_simple(self):
        input_data = 'include'
        expected = [
            Token(Keyword.INCLUDE, 1, 1)
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_include(self):
        input_data = '#include "script_component.hpp"'
        expected = [
            Token(Symbol.HASH, 1, 1),
            Token(Keyword.INCLUDE, 1, 2),
            Token(Symbol.WHITESPACE, 1, 9),
            Token(Symbol.DOUBLE_QUOTES, 1, 10),
            Token(Literal.STRING_LITERAL, 1, 11, "script_component.hpp"),
            Token(Symbol.DOUBLE_QUOTES, 1, 31)
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_string_literal1(self):
        input_data = 'hello'
        expected = [
            Token(Literal.STRING_LITERAL, 1, 1, 'hello')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_string_literal2(self):
        input_data = 'hello world'
        expected = [
            Token(Literal.STRING_LITERAL, 1, 1, 'hello'),
            Token(Symbol.WHITESPACE, 1, 6),
            Token(Literal.STRING_LITERAL, 1, 7, 'world')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_string_literal3(self):
        input_data = 'hello1234!'
        expected = [
            Token(Literal.STRING_LITERAL, 1, 1, 'hello1234!')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_number_literal1(self):
        input_data = '1234'
        expected = [
            Token(Literal.NUMBER_LITERAL, 1, 1, '1234')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_number_literal2(self):
        input_data = '12.34'
        expected = [
            Token(Literal.NUMBER_LITERAL, 1, 1, '12.34')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_number_literal3(self):
        input_data = '-1234'
        expected = [
            Token(Literal.NUMBER_LITERAL, 1, 1, '-1234')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_number_literal4(self):
        input_data = '-12.34'
        expected = [
            Token(Literal.NUMBER_LITERAL, 1, 1, '-12.34')
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_multiline1(self):
        input_data = '''#include "script_component.hpp"
class Foo {};'''
        expected = [
            Token(Symbol.HASH, 1, 1),
            Token(Keyword.INCLUDE, 1, 2),
            Token(Symbol.WHITESPACE, 1, 9),
            Token(Symbol.DOUBLE_QUOTES, 1, 10),
            Token(Literal.STRING_LITERAL, 1, 11, "script_component.hpp"),
            Token(Symbol.DOUBLE_QUOTES, 1, 31),
            Token(Symbol.NEWLINE, 1, 32),
            Token(Keyword.CLASS, 2, 1),
            Token(Symbol.WHITESPACE, 2, 6),
            Token(Literal.STRING_LITERAL, 2, 7, 'Foo'),
            Token(Symbol.WHITESPACE, 2, 10),
            Token(Symbol.L_CURLY, 2, 11),
            Token(Symbol.R_CURLY, 2, 12),
            Token(Symbol.SEMICOLON, 2, 13)
        ]
        tokens = Lexer(input_data).tokenize()
        self.assertEqual(tokens, expected)

    def test_file_sample01(self):
        with open("../examples/01_simple_config.cpp", 'r') as fp:
            input_data = fp.read()
        Lexer(input_data).tokenize()

    def test_file_sample02(self):
        with open("../examples/02_acex_rations_config.cpp", 'r') as fp:
            input_data = fp.read()
        Lexer(input_data).tokenize()
