import unittest

from armaclassparser.lexer import Lexer
from armaclassparser.preprocessor import PreProcessor


class TestPreProcessor(unittest.TestCase):
    def test_remove_single_line_comment1(self):
        input_data = '''#include "script_component.hpp" // Hello World
class Foo {};'''
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        len_before = len(tokens)
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(len_before - 5, len(preprocessor.tokens))

    def test_remove_single_line_comment2(self):
        input_data = '''// Hello World
class Foo {};'''
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        len_before = len(tokens)
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(len_before - 5, len(preprocessor.tokens))

    def test_remove_single_line_comment3(self):
        input_data = "// Hello World"
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(0, len(preprocessor.tokens))

    def test_remove_single_line_comment4(self):
        input_data = "// "
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(0, len(preprocessor.tokens))

    def test_remove_single_line_comment5(self):
        input_data = """
//
"""
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(2, len(preprocessor.tokens))

    def test_remove_single_line_comment6(self):
        input_data = """
// hello"""
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(1, len(preprocessor.tokens))

    def test_remove_multi_line_comment1(self):
        input_data = '''#include "script_component.hpp" /* Hello World */
class Foo {};'''
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        len_before = len(tokens)
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(len_before - 7, len(preprocessor.tokens))

    def test_remove_multi_line_comment2(self):
        input_data = '''/* Hello World */
class Foo {};'''
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        len_before = len(tokens)
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(len_before - 7, len(preprocessor.tokens))

    def test_remove_multi_line_comment3(self):
        input_data = "/* Hello World*/"
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(0, len(preprocessor.tokens))

    def test_remove_multi_line_comment4(self):
        input_data = "/**/"
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(0, len(preprocessor.tokens))

    def test_remove_multi_line_comment5(self):
        input_data = """
/* hello */
"""
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(2, len(preprocessor.tokens))

    def test_remove_multi_line_comment6(self):
        input_data = """
/* hello */"""
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(1, len(preprocessor.tokens))

    def test_remove_multi_line_comment7(self):
        input_data = """
/* hello 
        world */"""
        from armaclassparser import lexer
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, None)
        preprocessor.tokens = tokens
        preprocessor._remove_comments()
        self.assertEqual(1, len(preprocessor.tokens))