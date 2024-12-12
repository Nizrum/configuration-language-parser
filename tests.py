import unittest
from main import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_define_constant(self):
        line = "(def pi 3.14)"
        name, value = self.parser.define_constant(line)
        self.assertEqual(name, "pi")
        self.assertEqual(value, 3.14)
        self.assertIn("pi", self.parser.constants)
        self.assertEqual(self.parser.constants["pi"], 3.14)

    def test_evaluate_simple_expression(self):
        line = "!(2 3 +)"
        result = self.parser.evaluate_expression(line)
        self.assertEqual(result, 5)

    def test_evaluate_nested_expression(self):
        self.parser.constants = {"base": 4000}
        line = "!(base !(2000 568 -) +)"
        result = self.parser.evaluate_expression(line)
        self.assertEqual(result, 5432)

    def test_evaluate_with_constants(self):
        self.parser.constants = {"a": 5, "b": 10}
        line = "!(a b +)"
        result = self.parser.evaluate_expression(line)
        self.assertEqual(result, 15)

    def test_parse_key_value(self):
        line = "max_users = 100"
        key, value = self.parser.parse_key_value(line)
        self.assertEqual(key, "max_users")
        self.assertEqual(value, 100)

    def test_parse_string_value(self):
        value = "@\"Hello, world!\""
        result = self.parser.parse_value(value)
        self.assertEqual(result, "Hello, world!")

    def test_parse_array_value(self):
        value = '[!(!(4 sqrt) 1 -); !(187 13 -); !(@"some" @"_value" concat)]'
        result = self.parser.parse_value(value)
        self.assertEqual(result, [1, 174, "some_value"])

    def test_full_parsing(self):
        text = """
        (def base_salary 4000)
        (def deduction !(2000 568 -))
        total_salary = !(base_salary deduction +)
        """
        result = self.parser.parse(text)
        self.assertEqual(result["base_salary"], 4000)
        self.assertEqual(result["deduction"], 1432)
        self.assertEqual(result["total_salary"], 5432)

if __name__ == "__main__":
    unittest.main()
