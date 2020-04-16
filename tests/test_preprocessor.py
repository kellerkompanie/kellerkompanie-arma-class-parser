import os
import unittest

from armaclassparser import generator, lexer
from armaclassparser.lexer import Lexer
from armaclassparser.preprocessor import PreProcessor


class TestPreProcessor(unittest.TestCase):
    def _test_preprocessor(self, input_data, expected_output):
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        preprocessor = PreProcessor(tokens, lexer.STRING_INPUT_FILE)
        preprocessor.preprocess()
        output = generator.from_tokens(preprocessor.tokens)
        self.assertEqual(expected_output, output)

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
        with open(file_path, 'r', encoding='utf-8', newline=None) as fp:
            input_data = fp.read()
        tokens = Lexer(input_data, file_path).tokenize()
        preprocessor = PreProcessor(tokens, file_path)
        preprocessor.preprocess()
        tokens = preprocessor.tokens
        output = generator.from_tokens(tokens)

        expected_output = """1_include_test_file1_line1
1_include_test_file1_line2
1_include_test_file1_line3

1_include_test_file2_line1
1_include_test_file2_line2
1_include_test_file2_line3
class Foo {};
1_include_test_file3_line1
1_include_test_file3_line2
1_include_test_file3_line3"""

        self.assertEqual(expected_output, output)

    def test_include2(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "examples/include/02_include_test_config.cpp")
        with open(file_path, 'r', encoding='utf-8', newline=None) as fp:
            input_data = fp.read()
        tokens = Lexer(input_data, file_path).tokenize()
        preprocessor = PreProcessor(tokens, file_path)
        preprocessor.preprocess()
        output = generator.from_tokens(preprocessor.tokens)
        expected_output = "\ntest"
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

        self._test_preprocessor(input_data, expected_output)

    def test_ifdef1(self):
        input_data = """#define TEST
#ifdef TEST
#define A a
#else
#define A b
#endif
class A {};"""
        expected_output = "class a {};"
        self._test_preprocessor(input_data, expected_output)

    def test_ifndef1(self):
        input_data = """#define TEST
#ifndef TEST
#define A a
#else
#define A b
#endif
class A {};"""
        expected_output = "class b {};"
        self._test_preprocessor(input_data, expected_output)

    def test_macro_usage1(self):
        input_data = """#define TEST test
class TEST {};"""
        expected_output = "class test {};"
        self._test_preprocessor(input_data, expected_output)

    def test_macro_usage2(self):
        input_data = """#define TEST author = "Schwaggot";
class test {TEST};"""
        expected_output = 'class test {author = "Schwaggot";};'
        self._test_preprocessor(input_data, expected_output)

    def test_macro_with_args1(self):
        input_data = """#define EXP(x) x * x
class test {value = EXP(2);};"""
        expected_output = 'class test {value = 2 * 2;};'
        self._test_preprocessor(input_data, expected_output)

    def test_macro_with_args2(self):
        input_data = """#define MUL(x,y) x * y
class test {value = MUL(2,3);};"""
        expected_output = 'class test {value = 2 * 3;};'
        self._test_preprocessor(input_data, expected_output)

    def test_macro_with_args3(self):
        input_data = """#define ARR_1(x) {x}
#define ARR_2(x,y) {x,y}
#define ARR_3(x,y,z) {x,y,z}
class test {
    arr1[] = ARR_1(1234);
    arr2[] = ARR_2("hello", 1234, 13.45);
    arr3[] = ARR_3(test, {12, 14});    
};"""
        expected_output = """class test {
    arr1[] = {1234};
    arr2[] = {"hello", 1234, 13.45};
    arr3[] = {test, {12, 14}};    
};"""
        self._test_preprocessor(input_data, expected_output)

    def test_macro_with_args4(self):
        input_data = """#define ARR_1(x) {x}
#define ARR_2(x,y) {x,y}
class test {
    arr[] = ARR_1(1234)+ARR_2("hello", 1234, 13.45);
};"""
        expected_output = """class test {
    arr[] = {1234}+{"hello", 1234, 13.45};
};"""
        self._test_preprocessor(input_data, expected_output)

    def test_double(self):
        input_data = """#define DOUBLES(var1,var2) var1##_##var2
DOUBLES(acex,main)"""
        expected_output = "acex_main"
        self._test_preprocessor(input_data, expected_output)

    def test_nested1(self):
        input_data = """#define TEST test
#define A(x) a_##x##_##TEST
A(b)"""
        expected_output = "a_b_test"
        self._test_preprocessor(input_data, expected_output)

    def test_nested2(self):
        input_data = """#define PI 3.14
#define A(x) x*PI
A(b)"""
        expected_output = "b*3.14"
        self._test_preprocessor(input_data, expected_output)

    def test_nested3(self):
        input_data = """#define A(x) a_##x
#define B(x) b_##x
#define AB(x) A(B(x))
AB(y)"""
        expected_output = "a_b_y"
        self._test_preprocessor(input_data, expected_output)

    def test_nested4(self):
        input_data = """#define A(x) a_##x
#define B(x) b_##x
A(B(y))"""
        expected_output = "a_b_y"
        self._test_preprocessor(input_data, expected_output)

    def test_nested5(self):
        input_data = """#define A(x) a_##x
#define B(x) b_##x
#define C(x) c_##x
#define ABC(x) A(B(C(x)))
ABC(y)"""
        expected_output = "a_b_c_y"
        self._test_preprocessor(input_data, expected_output)

    def test_compile_file(self):
        input_data = """#define DOUBLES(var1,var2) var1##_##var2
#define QUOTE(var1) #var1
#define MAINPREFIX x
#define SUBPREFIX addons
#define PATHTO_SYS(var1,var2,var3) \\MAINPREFIX\\var1\\SUBPREFIX\\var2\\var3.sqf
#define COMPILE_FILE2_CFG_SYS(var1) compile preprocessFileLineNumbers var1
#define COMPILE_FILE2_SYS(var1) COMPILE_FILE2_CFG_SYS(var1)
#define COMPILE_FILE_SYS(var1,var2,var3) COMPILE_FILE2_SYS('PATHTO_SYS(var1,var2,var3)')
#define COMPILE_FILE_CFG_SYS(var1,var2,var3) COMPILE_FILE2_CFG_SYS('PATHTO_SYS(var1,var2,var3)')
#define COMPILE_FILE(var1) COMPILE_FILE_SYS(acex,rations,var1)
QUOTE(COMPILE_FILE(x))"""
        expected_output = '"compile preprocessFileLineNumbers \'\\x\\acex\\addons\\rations\\x.sqf\'"'
        self._test_preprocessor(input_data, expected_output)

    def test_quote(self):
        input_data = """#define QUOTE(var) #var
QUOTE(hello world)"""
        expected_output = '"hello world"'
        self._test_preprocessor(input_data, expected_output)
