# usagi lang interpreter

import re
import sys

from usagi.environment import Environment
from usagi.errors import UsagiError
from usagi.nodes import (
    Add,
    Assign,
    Divide,
    InputInt,
    Modulo,
    Multiply,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Variable,
)

# 문자 출력 유니코드 범위
MIN_CHAR_CODE = 1
MAX_CHAR_CODE = 0x10FFFF
SURROGATE_START = 0xD800
SURROGATE_END = 0xDFFF

INTEGER_INPUT = re.compile(r"-?[0-9]+")

def run(program, out=None, inp=None):
    Interpreter(out, inp).run(program)

def c_divide(left, right):
    # 나눗셈: 몫을 0 쪽으로 버린다. python의 //는 내림이기에 직접 계산
    quotient = abs(left) // abs(right)
    if(left < 0) != (right < 0):
        quotient = -quotient
    return quotient

def c_modulo(left, right):
    return left - right * c_divide(left, right)

class Interpreter:
    def __init__(self, out=None, inp=None):
        self.out = out if out is not None else sys.stdout
        self.inp = inp if inp is not None else sys.stdin
        self.env = Environment()

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

        elif isinstance(node, Assign):
            value = self.evaluate(node.expr)
            self.env.set(node.index, value)

        elif isinstance(node, InputInt):
            value = self.read_int(node.line)
            self.env.set(node.index, value)

        else:
            # 파서가 만들지 않는 노드가 들어온 경우 (인터프리터 버그)
            raise UsagiError(f"실행할 수 없는 문장: {type(node).__name__}", node.line)

    # 식
    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value

        if isinstance(node, Variable):
            return self.env.get(node.index, node.line)

        if isinstance(node, Multiply):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return left * right

        if isinstance(node, Add):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return left + right

        if isinstance(node, Divide):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            self.check_not_zero(right, node.line)
            return c_divide(left, right)

        if isinstance(node, Modulo):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            self.check_not_zero(right, node.line)
            return c_modulo(left, right)

        # 파서가 만들지 않는 노드가 들어온 경우 (인터프리터 버그)
        raise UsagiError(f"계산할 수 없는 식: {type(node).__name__}", node.line)

    # 도우미
    def check_not_zero(self, value, line):
        if value == 0:
            raise UsagiError("0으로 나눌 수 없음", line)

    def read_int(self, line):
        text = self.inp.readline()

        if text == "":
            raise UsagiError("더 읽을 입력이 없음", line)

        text = text.strip()
        if not INTEGER_INPUT.fullmatch(text):
            raise UsagiError(f"정수 입력에 숫자가 아닌 값: {text}", line)
        return int(text)

    def to_char(self, code, line):
        if code < MIN_CHAR_CODE or code > MAX_CHAR_CODE:
            raise UsagiError(f"출력할 수 없는 문자 코드: {code}", line)
        if SURROGATE_START <= code <= SURROGATE_END:
            raise UsagiError(f"출력할 수 없는 문자 코드: {code}", line)
        return chr(code)

    def write(self, text):
        self.out.write(text)