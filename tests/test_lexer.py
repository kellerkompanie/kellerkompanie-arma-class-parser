import os
import unittest

import armaclassparser
from armaclassparser import lexer
from armaclassparser.lexer import Token, TokenType, Lexer


class TestLexer(unittest.TestCase):

    def test_next(self):
        input_data = 'hello'
        lexer = Lexer(input_data, armaclassparser.lexer.STRING_INPUT_FILE)
        self.assertEqual('h', lexer.next())
        self.assertEqual('e', lexer.next())
        self.assertEqual('l', lexer.next())
        self.assertEqual('l', lexer.next())
        self.assertEqual('o', lexer.next())
        try:
            lexer.next()
            self.fail('expected exception')
        except RuntimeError:
            pass

    def test_peek(self):
        input_data = 'hello'
        lexer = Lexer(input_data, armaclassparser.lexer.STRING_INPUT_FILE)
        self.assertEqual('h', lexer.peek())
        self.assertEqual('h', lexer.peek(1))
        self.assertEqual('he', lexer.peek(2))
        self.assertEqual('hello', lexer.peek(5))

    def test_class_simple(self):
        input_data = 'class'
        expected = [
            Token(TokenType.KEYWORD_CLASS, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1)
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_class(self):
        input_data = 'class Foo {};'
        expected = [
            Token(TokenType.KEYWORD_CLASS, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 6),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 7, 'Foo'),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 10),
            Token(TokenType.L_CURLY, armaclassparser.lexer.STRING_INPUT_FILE, 1, 11),
            Token(TokenType.R_CURLY, armaclassparser.lexer.STRING_INPUT_FILE, 1, 12),
            Token(TokenType.SEMICOLON, armaclassparser.lexer.STRING_INPUT_FILE, 1, 13)
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_include_simple(self):
        input_data = '#include'
        expected = [
            Token(TokenType.KEYWORD_INCLUDE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1)
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_include(self):
        input_data = '#include "script_component.hpp"'
        expected = [
            Token(TokenType.KEYWORD_INCLUDE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 9),
            Token(TokenType.DOUBLE_QUOTES, armaclassparser.lexer.STRING_INPUT_FILE, 1, 10),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 11, "script_component"),
            Token(TokenType.DOT, armaclassparser.lexer.STRING_INPUT_FILE, 1, 27),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 28, "hpp"),
            Token(TokenType.DOUBLE_QUOTES, armaclassparser.lexer.STRING_INPUT_FILE, 1, 31)
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_string_literal1(self):
        input_data = 'hello'
        expected = [
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, 'hello')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_string_literal2(self):
        input_data = 'hello world'
        expected = [
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, 'hello'),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 6),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 7, 'world')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_string_literal3(self):
        input_data = 'hello1234!'
        expected = [
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, 'hello1234!')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_number_literal1(self):
        input_data = '1234'
        expected = [
            Token(TokenType.NUMBER, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, '1234')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_number_literal2(self):
        input_data = '12.34'
        expected = [
            Token(TokenType.NUMBER, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, '12.34')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_number_literal3(self):
        input_data = '-1234'
        expected = [
            Token(TokenType.NUMBER, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, '-1234')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_number_literal4(self):
        input_data = '-12.34'
        expected = [
            Token(TokenType.NUMBER, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1, '-12.34')
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_multiline1(self):
        input_data = '''#include "script_component.hpp"
class Foo {};'''
        expected = [
            Token(TokenType.KEYWORD_INCLUDE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 1),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 9),
            Token(TokenType.DOUBLE_QUOTES, armaclassparser.lexer.STRING_INPUT_FILE, 1, 10),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 11, "script_component"),
            Token(TokenType.DOT, armaclassparser.lexer.STRING_INPUT_FILE, 1, 27),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 1, 28, "hpp"),
            Token(TokenType.DOUBLE_QUOTES, armaclassparser.lexer.STRING_INPUT_FILE, 1, 31),
            Token(TokenType.NEWLINE, armaclassparser.lexer.STRING_INPUT_FILE, 1, 32),
            Token(TokenType.KEYWORD_CLASS, armaclassparser.lexer.STRING_INPUT_FILE, 2, 1),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 2, 6),
            Token(TokenType.WORD, armaclassparser.lexer.STRING_INPUT_FILE, 2, 7, 'Foo'),
            Token(TokenType.WHITESPACE, armaclassparser.lexer.STRING_INPUT_FILE, 2, 10),
            Token(TokenType.L_CURLY, armaclassparser.lexer.STRING_INPUT_FILE, 2, 11),
            Token(TokenType.R_CURLY, armaclassparser.lexer.STRING_INPUT_FILE, 2, 12),
            Token(TokenType.SEMICOLON, armaclassparser.lexer.STRING_INPUT_FILE, 2, 13)
        ]
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        self.assertEqual(expected, tokens)

    def test_file_sample01(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "examples/01_simple_config.cpp")
        with open(file_path, 'r', encoding='utf-8', newline=None) as fp:
            input_data = fp.read()
        Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
