# usagi lang interpreter

import sys

from usagi.errors import UsagiError
from usagi.nodes import Multiply, Number, Print, PrintChar, PrintNoNewline

# 문자 출력 유니코드 범위
MIN_CHAR_CODE = 1
MAX_CHAR_CODE = 0x10FFFF
SURROGATE_START = 0xD800
SURROGATE_END = 0xDFFF

def run(program, out=None):
    Interpreter(out).run(program)

class Interpreter:
    def __init__(self, out=None):
        self.out = out if out is not None else sys.stdout

    # 프로그램과 함수
    def run(self, program):
        self.run_function(program.main)

    def run_function(self, function):
        for statement in function.body:
            self.execute(statement)

    # 문장
    def execute(self, node):
        if isinstance(node, Print):
            value = self.evaluate(node.expr)
            self.write(str(value) + "\n")

        elif isinstance(node, PrintNoNewline):
            value = self.evaluate(node.expr)
            self.write(str(value))

        elif isinstance(node, PrintChar):
            value = self.evaluate(node.expr)
            self.write(self.to_char(value, node.line))

        else:
            # 파서가 만들지 않는 노드가 들어온 경우 (인터프리터 버그)
            raise UsagiError(f"실행할 수 없는 문장: {type(node).__name__}", node.line)

    # 식
    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value

        if isinstance(node, Multiply):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return left * right

        # 파서가 만들지 않는 노드가 들어온 경우 (인터프리터 버그)
        raise UsagiError(f"계산할 수 없는 식: {type(node).__name__}", node.line)

    # 도우미
    def to_char(self, code, line):
        if code < MIN_CHAR_CODE or code > MAX_CHAR_CODE:
            raise UsagiError(f"출력할 수 없는 문자 코드: {code}", line)
        if SURROGATE_START <= code <= SURROGATE_END:
            raise UsagiError(f"출력할 수 없는 문자 코드: {code}", line)
        return chr(code)

    def write(self, text):
        self.out.write(text)