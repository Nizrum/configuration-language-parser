import argparse
import json
import re
import math
import sys

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        lines = text.splitlines()
        result = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("'"):
                continue

            if line.startswith('(def'):
                name, value = self.define_constant(line)
                result[name] = value
            elif line.startswith('!('):
                value = self.evaluate_expression(line)
                if value is not None:
                    if 'evaluated' in result:
                      result['evaluated'].append(value)
                    else:
                        result['evaluated'] = [value]

        return result

    def define_constant(self, line):
        match = re.match(r'\(def\s+(\w+)\s+(.+)\)', line)
        if not match:
            raise ValueError(f"Некорректное определение константы: {line}")
        name, value = match.groups()
        self.constants[name] = self.parse_value(value)
        return name, self.parse_value(value)

    def evaluate_expression(self, line):
        match = re.match(r'!\((.+)\)', line)
        if not match:
            raise ValueError(f"Invalid expression: {line}")
        
        expression = match.group(1).strip()
        tokens = self.tokenize_expression(expression)
        stack = []

        for token in tokens:
            if token in self.constants:  # Константа
                stack.append(self.constants[token])
            elif token == '+':
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            elif token == '-':
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            elif token == 'concat':
                b = stack.pop()
                a = stack.pop()
                if (type(a) is list and type(b) is list):
                    stack.append(a + b)
                elif type(a) is list:
                    a.append(b)
                    stack.append(a)
                elif type(b) is list:
                    b.insert(0, a)
                    stack.append(b)
                else:
                    stack.append(str(a) + str(b))
            elif token == 'sqrt':
                a = stack.pop()
                stack.append(math.sqrt(a))
            else:
                stack.append(self.parse_value(token))

        if len(stack) != 1:
            raise ValueError("Invalid expression result")

        return stack.pop()

    def tokenize_expression(self, expression):
        """Разбивает выражение на токены, учитывая вложенность."""
        tokens = []
        buffer = ''
        depth = 0

        for char in expression:
            if char == '(' or char == '[':
                depth += 1
                buffer += char
            elif char == ')' or char == ']':
                depth -= 1
                buffer += char
                if depth == 0:
                    tokens.append(buffer)
                    buffer = ''
            elif char == ' ' and depth == 0:
                if buffer:
                    tokens.append(buffer)
                    buffer = ''
            else:
                buffer += char

        if buffer:
            tokens.append(buffer)
        return tokens

    def parse_value(self, value):
        value = value.strip()

        if re.match(r'^[\d\.]+$', value):
            return float(value)
        elif re.match(r'^@\".*\"$', value):
            return value[2:-1]
        elif re.match(r'^\[.*\]$', value):
            items = value[1:-1].split(';')
            return [self.parse_value(item) for item in items]
        elif re.match(r'^!\(.*\)$', value):
            return self.evaluate_expression(value)
        else:
            raise ValueError(f"Некорректное значение: {value}")

def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык в JSON.")
    parser.add_argument('input_file', help="Путь к входному файлу.")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as file:
            text = file.read()

        config_parser = ConfigParser()
        result = config_parser.parse(text)
        print(json.dumps(result, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    main()
