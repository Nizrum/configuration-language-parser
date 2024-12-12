import argparse
import json
import re
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

        return result

    def define_constant(self, line):
        match = re.match(r'\(def\s+(\w+)\s+(.+)\)', line)
        if not match:
            raise ValueError(f"Некорректное определение константы: {line}")
        name, value = match.groups()
        self.constants[name] = self.parse_value(value)
        return name, self.parse_value(value)

    def parse_value(self, value):
        value = value.strip()

        if re.match(r'^\d+$', value):
            return int(value)
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
