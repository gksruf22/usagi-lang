# parser test

import pytest

from usagi.errors import UsagiError
from usagi.lexer import tokenize
from usagi.nodes import (
    Function,
    Multiply,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Program,
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