import os
import unittest

from armaclassparser import generator, lexer
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
        preprocessor._replace_includes(recursive=False)
        tokens = preprocessor.tokens
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
        preprocessor._replace_includes(recursive=False)
        output = generator.from_tokens(preprocessor.tokens)
        expected_output = "#define TEST test"
        self.assertEqual(expected_output, output)

    def test_escaped_newlines(self):
        input_data = """\\
"""
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, lexer.STRING_INPUT_FILE)
        preprocessor._remove_escaped_newlines()
        output = generator.from_tokens(preprocessor.tokens)
        expected_output = ""
        self.assertEqual(expected_output, output)

    def test_define1(self):
        input_data = """#define DEBUG_SYNCHRONOUS

#define ADDON test_addon
// Default versioning level
#define DEFAULT_VERSIONING_LEVEL 2

// weapon types
#define TYPE_WEAPON_PRIMARY 1
#define TYPE_WEAPON_HANDGUN 2
#define TYPE_WEAPON_SECONDARY 4
// more types
#define TYPE_BINOCULAR_AND_NVG 4096
#define TYPE_WEAPON_VEHICLE 65536
#define TYPE_ITEM 131072

#define ACE_isHC (!hasInterface && !isDedicated)

#define IDC_STAMINA_BAR 193
#define GRAVITY 9.8066

class CfgPatches {
    class ADDON {
        type = TYPE_BINOCULAR_AND_NVG;
        version = DEFAULT_VERSIONING_LEVEL;
        condition = "ACE_isHC";
        types = {
            TYPE_WEAPON_PRIMARY,
            TYPE_WEAPON_HANDGUN,
            TYPE_WEAPON_SECONDARY,
            TYPE_BINOCULAR_AND_NVG,
            TYPE_WEAPON_VEHICLE,
            TYPE_ITEM
        };
        value = IDC_STAMINA_BAR+GRAVITY;
    };
};"""
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, lexer.STRING_INPUT_FILE)
        tokens = preprocessor.preprocess()
        preprocessor.preprocess()
        output = generator.from_tokens(tokens)
        expected_output = """







class CfgPatches {
    class test_addon {
        type = 4096;
        version = 2;
        condition = "(!hasInterface && !isDedicated)";
        types = {
            1,
            2,
            4,
            4096,
            65536,
            131072
        };
        value = 193+9.8066;
    };
};"""

        self.assertEqual(expected_output, output)