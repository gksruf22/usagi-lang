# usagi lang AST 노드

from dataclasses import dataclass

# 식

@dataclass
class Number:
    value: int
    line: int

@dataclass
class Variable:
    index: int
    line: int

@dataclass
class Multiply:
    left: object
    right: object
    line: int

@dataclass
class Divide:
    left: object
    right: object
    line: int

@dataclass
class Modulo:
    left: object
    right: object
    line: int

@dataclass
class Add:
    left: object
    right: object
    line: int

# 문장

@dataclass
class Print:
    expr: object
    line: int

@dataclass
class PrintNoNewline:
    expr: object
    line: int

@dataclass
class PrintChar:
    expr: object
    line: int

@dataclass
class Assign:
    index: int
    expr: object
    line: int

@dataclass
class InputInt:
    index: int
    line: int

# 함수와 프로그램

@dataclass
class Function:
    name: str
    param_count: int
    body: list
    line: int

@dataclass
class Program:
    main: Function