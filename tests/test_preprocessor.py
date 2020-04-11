import os
import unittest

from armaclassparser import generator
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

    def test_include1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "examples/include/01_include_test_config.cpp")
        with open(file_path, 'r') as fp:
            input_data = fp.read()
        tokens = Lexer(input_data, file_path).tokenize()
        preprocessor = PreProcessor(tokens, file_path)
        tokens = preprocessor.preprocess()
        output = generator.from_tokens(tokens)

        expected_output = """#define TEST_FILE1_1 01_include_test_file1_line1
#define TEST_FILE1_2 01_include_test_file1_line2
#define TEST_FILE1_3 01_include_test_file1_line3

#define TEST_FILE2_1 01_include_test_file2_line1
#define TEST_FILE2_2 01_include_test_file2_line2
#define TEST_FILE2_3 01_include_test_file2_line3
class Foo {};
#define TEST_FILE3_1 01_include_test_file3_line1
#define TEST_FILE3_2 01_include_test_file3_line2
#define TEST_FILE3_3 01_include_test_file3_line3"""

        self.assertEqual(expected_output, output)

    def test_include2(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "examples/include/02_include_test_config.cpp")
        with open(file_path, 'r') as fp:
            input_data = fp.read()
        tokens = Lexer(input_data, file_path).tokenize()
        preprocessor = PreProcessor(tokens, file_path)
        tokens = preprocessor.preprocess()
        output = generator.from_tokens(tokens)

        expected_output = "#define TEST test"

        self.assertEqual(expected_output, output)
