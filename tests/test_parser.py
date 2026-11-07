# parser test

import pytest

from usagi.errors import UsagiError
from usagi.lexer import tokenize
from usagi.nodes import (
    Add,
    Assign,
    Divide,
    Function,
    InputInt,
    Modulo,
    Multiply,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Program,
    Variable,
)
from usagi.parser import parse

def parse_source(source):
    return parse(tokenize(source))


# 정상

def test_빈메인블록():
    program = parse_source("미야아아\n야하핫")
    assert isinstance(program, Program)
    assert program.main == Function("main", 0, [], 1)

def test_출력문():
    program = parse_source("미야아아\n야하 우라\n야핫 우라라\n루루루루루 우라라라\n야하핫")
    body = program.main.body
    assert body == [
        Print(Number(1, 2), 2),
        PrintNoNewline(Number(2, 3), 3),
        PrintChar(Number(3, 4), 4),
    ]

def test_곱하기_묶기():
    program = parse_source("미야아아\n야하 우라라 우라라라 우라라라라\n야하핫")
    expr = program.main.body[0].expr
    assert expr == Multiply(Multiply(Number(2, 2), Number(3, 2), 2), Number(4, 2), 2) 

def test_메인앞뒤_주석_빈줄():
    source = "푸루야우라우라 시작\n\n미야아아\n야하 우\n야하핫\n\n푸루야우라우라 끝"
    program = parse_source(source)
    assert program.main.body == [Print(Number(0, 4), 4)]


# 에러
@pytest.mark.parametrize(
    "source, line, message",
    [
        ("", None, "메인 블록(미야아아)이 없음"),
        ("야하 우라", None, "메인 블록(미야아아)이 없음"),
        ("야하 우라\n미야아아\n야하핫", 1, "메인 블록 밖에 문장이 있음"),
        ("미야아아\n야하핫\n야하 우라", 3, "메인 블록 밖에 문장이 있음"),
        ("미야아아\n야하핫\n미야아아\n야하핫", 3, "메인 블록이 두 개 있음"),
        ("미야아아\n야하 우라", 1, "블록 끝(야하핫)이 없음"),
        ("미야아아 야하\n야하핫", 1, "메인 시작(미야아아) 뒤에 다른 단어가 있음"),
        ("미야아아\n야하핫 우라", 2, "블록 끝(야하핫) 뒤에 다른 단어가 있음"),
        ("미야아아\n야하\n야하핫", 2, "출력할 값이 없음"),
        ("미야아아\n우라\n야하핫", 2, "문장을 시작할 수 없는 단어"),
        ("미야아아\n야하 우라 야하 우라\n야하핫", 2, "한 줄에 문장은 하나만 쓸 수 있음"),
    ],
)
def test_문법에러(source, line, message):
    with pytest.raises(UsagiError) as info:
        parse_source(source)
    assert info.value.line == line
    assert info.value.message == message


# 2단계

def first_expr(code):
    return parse_source(f"미야아아\n야하 {code}\n야하핫").main.body[0].expr
 
 
def test_대입문():
    body = parse_source("미야아아\n푸루 흐응 우라라\n야하핫").main.body
    assert body == [Assign(1, Number(2, 2), 2)]
 
 
def test_입력문():
    body = parse_source("미야아아\n쥬르리 푸루루\n야하핫").main.body
    assert body == [InputInt(2, 2)]
 
 
def test_변수_읽기():
    assert first_expr("푸루루") == Variable(2, 2)
 
 
def test_곱하기_먼저():
    assert first_expr("우라 이야 우라라 우라라라") == Add(
        Number(1, 2), Multiply(Number(2, 2), Number(3, 2), 2), 2
    )
 
 
def test_더하기는_왼쪽부터():
    assert first_expr("우라 이야 우라라 이야 우라라라") == Add(
        Add(Number(1, 2), Number(2, 2), 2), Number(3, 2), 2
    )
 
 
def test_곱하기_나누기_왼쪽부터():
    assert first_expr("우라라라 우라라라라라우라라 이야 우라") == Add(
        Divide(Multiply(Number(3, 2), Number(5, 2), 2), Number(2, 2), 2),
        Number(1, 2),
        2,
    )
 
 
def test_나머지():
    assert first_expr("우라라라라라라라 핫 우라라라") == Modulo(Number(7, 2), Number(3, 2), 2)
 
 
def test_빼기_음수_곱하고더하기():
    assert first_expr("우라라라라라 이야 우루 우라라") == Add(
        Number(5, 2), Multiply(Number(-1, 2), Number(2, 2), 2), 2
    )
 
 
@pytest.mark.parametrize(
    "source, line, message",
    [
        ("미야아아\n푸루 흐응\n야하핫", 2, "넣을 값이 없음"),
        ("미야아아\n푸루우라 흐응 우라\n야하핫", 2, "값을 넣을 곳은 변수 하나여야 함"),
        ("미야아아\n푸루\n야하핫", 2, "문장을 시작할 수 없는 단어"),
        ("미야아아\n푸루 우라\n야하핫", 2, "문장을 시작할 수 없는 단어"),
        ("미야아아\n쥬르리\n야하핫", 2, "입력을 넣을 곳은 변수 하나여야 함"),
        ("미야아아\n쥬르리 우라\n야하핫", 2, "입력을 넣을 곳은 변수 하나여야 함"),
        ("미야아아\n쥬르리 푸루우라\n야하핫", 2, "입력을 넣을 곳은 변수 하나여야 함"),
        ("미야아아\n쥬르리 푸루 푸루루\n야하핫", 2, "한 줄에 문장은 하나만 쓸 수 있음"),
        ("미야아아\n야하 우라 이야\n야하핫", 2, "계산할 값이 없음"),
        ("미야아아\n야하 우라 핫\n야하핫", 2, "계산할 값이 없음"),
        ("미야아아\n야하 이야 우라\n야하핫", 2, "출력할 값이 없음"),
        ("미야아아\n야하 우라 이야 핫 우라\n야하핫", 2, "계산할 값이 없음"),
        ("미야아아\n흐응 우라\n야하핫", 2, "문장을 시작할 수 없는 단어"),
    ],
)
def test_2단계_문법에러(source, line, message):
    with pytest.raises(UsagiError) as info:
        parse_source(source)
    assert info.value.line == line
    assert info.value.message == message