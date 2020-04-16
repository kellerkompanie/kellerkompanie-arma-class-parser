import unittest

import armaclassparser
from armaclassparser import lexer, generator
from armaclassparser.lexer import Lexer


class TestGenerator(unittest.TestCase):

    def _test_generator_tokens(self, input_data, expected_output):
        tokens = Lexer(input_data, lexer.STRING_INPUT_FILE).tokenize()
        output = generator.from_tokens(tokens)
        self.assertEqual(expected_output, output)

    def _test_generator_ast(self, input_data, expected_output):
        ast = armaclassparser.parse_from_string(input_data)
        output = generator.from_ast(ast)
        self.assertEqual(expected_output, output)

    def test_number1(self):
        input_data = "1"
        expected_output = "1"
        self._test_generator_tokens(input_data, expected_output)

    def test_number2(self):
        input_data = "-1"
        expected_output = "-1"
        self._test_generator_tokens(input_data, expected_output)

    def test_number3(self):
        input_data = "1234"
        expected_output = "1234"
        self._test_generator_tokens(input_data, expected_output)

    def test_number4(self):
        input_data = "12.34"
        expected_output = "12.34"
        self._test_generator_tokens(input_data, expected_output)

    def test_number5(self):
        input_data = "-12.34"
        expected_output = "-12.34"
        self._test_generator_tokens(input_data, expected_output)

    def test_class1(self):
        input_data = "class Foo {};"
        expected_output = "class Foo {};"
        self._test_generator_tokens(input_data, expected_output)

        input_data = "class Foo {};"
        expected_output = """class Foo {
};"""
        self._test_generator_ast(input_data, expected_output)
