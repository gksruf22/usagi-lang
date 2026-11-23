# parser test

import pytest

from usagi.errors import UsagiError
from usagi.lexer import tokenize
from usagi.nodes import (
    Add,
    Assign,
    Break,
    Continue,
    Divide,
    Equal,
    Function,
    Greater,
    If,
    InputInt,
    Less,
    Modulo,
    Multiply,
    Not,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Program,
    Variable,
    While,
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

# 3단계

def main_body(*lines):
    return parse_source("미야아아\n" + "\n".join(lines) + "\n야하핫").main.body


# 비교와 NOT

@pytest.mark.parametrize(
    "word, node_class",
    [
        ("우나", Equal),
        ("우-라-", Greater),
        ("-라-우", Less),
    ],
)
def test_비교(word, node_class):
    assert first_expr(f"우라 {word} 우라라") == node_class(Number(1, 2), Number(2, 2), 2)


def test_비교는_더하기보다_나중():
    # 우라 이야 우라 우나 우라라 = (1 + 1) == 2
    assert first_expr("우라 이야 우라 우나 우라라") == Equal(
        Add(Number(1, 2), Number(1, 2), 2), Number(2, 2), 2
    )


def test_비교는_곱하기보다_나중():
    # 푸루 우-라- 우 푸루 = 푸루 > (0 × 푸루)
    assert first_expr("푸루 우-라- 우 푸루") == Greater(
        Variable(1, 2), Multiply(Number(0, 2), Variable(1, 2), 2), 2
    )


def test_비교_이어쓰면_왼쪽부터():
    # 우라 우나 우라 우나 우라 = (1 == 1) == 1
    assert first_expr("우라 우나 우라 우나 우라") == Equal(
        Equal(Number(1, 2), Number(1, 2), 2), Number(1, 2), 2
    )


def test_NOT은_가장_나중():
    # 우-이- 우라 우나 우라 = NOT (1 == 1)
    assert first_expr("우-이- 우라 우나 우라") == Not(
        Equal(Number(1, 2), Number(1, 2), 2), 2
    )


def test_NOT_두번():
    assert first_expr("우-이- 우-이- 우라") == Not(Not(Number(1, 2), 2), 2)


def test_비교_결과를_대입():
    assert main_body("푸루 흐응 우라 -라-우 우라라") == [
        Assign(1, Less(Number(1, 2), Number(2, 2), 2), 2)
    ]


# 조건문

def test_조건문():
    body = main_body(
        "하? 푸루 우나 우",
        "야하 우라",
        "야하핫",
    )
    assert body == [
        If(Equal(Variable(1, 2), Number(0, 2), 2), [Print(Number(1, 3), 3)], [], 2)
    ]


def test_조건문_아니면():
    body = main_body(
        "하? 푸루",
        "야하 우라",
        "하아?",
        "야하 우라라",
        "야핫 우라라라",
        "야하핫",
    )
    assert body == [
        If(
            Variable(1, 2),
            [Print(Number(1, 3), 3)],
            [Print(Number(2, 5), 5), PrintNoNewline(Number(3, 6), 6)],
            2,
        )
    ]


def test_빈_조건문():
    assert main_body("하? 우라", "하아?", "야하핫") == [If(Number(1, 2), [], [], 2)]


def test_조건문_뒤에_문장():
    body = main_body("하? 우라", "야하핫", "야하 우라라")
    assert body == [If(Number(1, 2), [], [], 2), Print(Number(2, 4), 4)]


def test_아니면_만약은_겹쳐쓰기():
    body = main_body(
        "하? 푸루 우나 우라",
        "야하 우라",
        "하아?",
        "하? 푸루 우나 우라라",
        "야하 우라라",
        "야하핫",
        "야하핫",
    )
    inner = If(Equal(Variable(1, 5), Number(2, 5), 5), [Print(Number(2, 6), 6)], [], 5)
    assert body == [
        If(Equal(Variable(1, 2), Number(1, 2), 2), [Print(Number(1, 3), 3)], [inner], 2)
    ]


# 반복문

def test_반복문():
    body = main_body(
        "푸루야 우-이- 푸루 우-라- 우라라라",
        "야하 푸루",
        "푸루 흐응 푸루 이야 우라",
        "야하핫",
    )
    condition = Not(Greater(Variable(1, 2), Number(3, 2), 2), 2)
    assert body == [
        While(
            condition,
            [
                Print(Variable(1, 3), 3),
                Assign(1, Add(Variable(1, 4), Number(1, 4), 4), 4),
            ],
            2,
        )
    ]


def test_탈출_건너뛰기():
    body = main_body("푸루야 우라", "하아아앗!", "으핫!", "야하핫")
    assert body == [While(Number(1, 2), [Break(3), Continue(4)], 2)]


def test_반복문_안_조건문_안의_탈출():
    body = main_body("푸루야 우라", "하? 우라", "하아아앗!", "야하핫", "야하핫")
    assert body == [While(Number(1, 2), [If(Number(1, 3), [Break(4)], [], 3)], 2)]


def test_반복문_겹치기():
    body = main_body("푸루야 우라", "푸루야 우라", "으핫!", "야하핫", "하아아앗!", "야하핫")
    assert body == [
        While(Number(1, 2), [While(Number(1, 3), [Continue(4)], 3), Break(6)], 2)
    ]


# 3단계 에러

@pytest.mark.parametrize(
    "lines, line, message",
    [
        # 조건이 없음
        (["하?", "야하핫"], 2, "조건이 없음"),
        (["푸루야", "야하핫"], 2, "조건이 없음"),
        # 비교·NOT 뒤에 값이 없음
        (["야하 우라 우나"], 2, "비교할 값이 없음"),
        (["야하 우라 -라-우 이야 우라"], 2, "비교할 값이 없음"),
        (["야하 우-이-"], 2, "비교할 값이 없음"),
        (["하? 우-이-", "야하핫"], 2, "비교할 값이 없음"),
        # 하아?
        (["하아?"], 2, "하?(조건문) 없이 하아?를 사용함"),
        (["하? 우라", "하아?", "하아?", "야하핫"], 4, "하?(조건문) 없이 하아?를 사용함"),
        (["푸루야 우라", "하아?", "야하핫"], 3, "하?(조건문) 없이 하아?를 사용함"),
        (["하? 우라", "하아? 우라", "야하핫"], 3, "하아? 뒤에 다른 단어가 있음"),
        # 탈출·건너뛰기 위치
        (["하아아앗!"], 2, "반복문 밖에서 하아아앗!을 사용함"),
        (["으핫!"], 2, "반복문 밖에서 으핫!을 사용함"),
        (["하? 우라", "하아아앗!", "야하핫"], 3, "반복문 밖에서 하아아앗!을 사용함"),
        (["푸루야 우라", "야하핫", "으핫!"], 4, "반복문 밖에서 으핫!을 사용함"),
        # 한 줄에 여러 개
        (["하? 우라 야하 우라", "야하핫"], 2, "한 줄에 문장은 하나만 쓸 수 있음"),
        (["푸루야 우라", "하아아앗! 우라", "야하핫"], 3, "한 줄에 문장은 하나만 쓸 수 있음"),
    ],
)
def test_3단계_문법에러(lines, line, message):
    source = "미야아아\n" + "\n".join(lines) + "\n야하핫"
    with pytest.raises(UsagiError) as info:
        parse_source(source)
    assert info.value.line == line
    assert info.value.message == message


def test_안쪽_블록_끝이_없으면_그_블록_줄():
    # 마지막까지 야하핫이 하나도 없으면, 가장 안쪽 블록(하?)의 줄을 알려준다
    with pytest.raises(UsagiError) as info:
        parse_source("미야아아\n하? 우라\n야하 우라")
    assert info.value.line == 2
    assert info.value.message == "블록 끝(야하핫)이 없음"


def test_야하핫이_하나_모자라면_메인_줄():
    # 조건문의 야하핫을 빠뜨리면 메인의 야하핫이 조건문을 닫는다.
    # 그래서 메인 블록이 닫히지 않은 것으로 보여 메인의 줄(1)을 알려준다.
    with pytest.raises(UsagiError) as info:
        parse_source("미야아아\n하? 우라\n야하 우라\n야하핫")
    assert info.value.line == 1
    assert info.value.message == "블록 끝(야하핫)이 없음"
