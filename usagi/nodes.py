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

@dataclass
class Equal:
    left: object
    right: object
    line: int

@dataclass
class Greater:
    left: object
    right: object
    line:  int

@dataclass
class Less:
    left: object
    right: object
    line: int

@dataclass
class Not:
    expr: object
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

@dataclass
class If:
    condition: object
    then_body: list # 참일 때 실행할 문장들
    else_body: list # 거짓일 때 실행할 문장들 (하아?가 없으면 빈 목록)
    line: int

@dataclass
class While:
    condition: object
    body: list
    line: int

@dataclass
class Break:
    line: int

@dataclass
class Continue:
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