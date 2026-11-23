# lexer test

import unicodedata

import pytest

from usagi.errors import UsagiError
from usagi.keywords import (
    ADD,
    ASSIGN,
    BLOCK_END,
    BREAK,
    CONTINUE,
    DIVIDE,
    ELSE,
    EQUAL,
    GREATER,
    IF,
    INPUT_INT,
    LESS,
    MAIN,
    MODULO,
    NEWLINE,
    NOT,
    NUMBER,
    PRINT,
    PRINT_CHAR,
    PRINT_NO_NEWLINE,
    VARIABLE,
    WHILE,
)
from usagi.lexer import normalize, read_source, tokenize

def kinds(tokens):
    return [token.kind for token in tokens]

# 키워드
def test_키워드():
    tokens = tokenize("미야아아\n야하\n야핫\n루루루루루\n야하핫")
    assert kinds(tokens) == [
        MAIN, NEWLINE,
        PRINT, NEWLINE,
        PRINT_NO_NEWLINE, NEWLINE,
        PRINT_CHAR, NEWLINE,
        BLOCK_END, NEWLINE,
    ]

# 정수
@pytest.mark.parametrize(
    "word, expected",
    [
        ("우", 0),
        ("우라", 1),
        ("우라라라", 3),
        ("우루", -1),
        ("우루루", -2),
    ],
)

def test_정수(word, expected):
    token = tokenize(word)[0]
    assert token.kind == NUMBER
    assert token.value == expected

def test_곱하기_정수토큰():
    tokens = tokenize("야하 우라라 우라라라")
    assert kinds(tokens) == [PRINT, NUMBER, NUMBER, NEWLINE]
    assert [t.value for t in tokens[1:3]] == [2, 3]

# 줄, 공백, 주석
def test_빈줄_주석_버리기():
    source = "미야아아\n\n푸루야우라우라 설명 \n야하 우라\n야하핫"
    tokens = tokenize(source)
    assert kinds(tokens) == [MAIN, NEWLINE, PRINT, NUMBER, NEWLINE, BLOCK_END, NEWLINE]
    assert [t.line for t in tokens if t.kind == NEWLINE] == [1, 4, 5]

def test_들여쓰기_탭_공백여러칸():
    tokens = tokenize("\t  야하   우라\t\t우라라  ")
    assert kinds(tokens) == [PRINT, NUMBER, NUMBER, NEWLINE]

# 정규화
@pytest.mark.parametrize(
    "before, after",
    [
        ("우ー라", "우-라"),   # 일본어 장음 부호
        ("우－라", "우-라"),   # 전각 하이픈
        ("우〜라", "우~라"),   # 물결 대시
        ("우～라", "우~라"),   # 전각 물결
        ("우∼라", "우~라"),   # 수학 물결
        ("하？", "하?"),       # 전각 물음표
    ],
)

def test_비슷한기호_통일(before, after):
    assert normalize(before) == after

def test_자모분리():
    source = unicodedata.normalize("NFD", "푸루야우라우라 맥\n 야하 우라라")
    assert kinds(tokenize(source)) == [PRINT, NUMBER, NEWLINE]

# 에러
@pytest.mark.parametrize(
    "word",
    [
        "우라루", # 리, 루 섞임
        "우-라",  # 끝의 -가 빠진 비교 키워드
        "루루루루", # 문자 출력 키워드(루루루루루)
        "야하야", # 키워드 뒤에 추가된 글자
        "우라라a", # 다른 글자가 섞임
    ],
)

def test_알수없는단어(word):
    with pytest.raises(UsagiError) as info:
        tokenize(f"미야아아\n야하 {word}")
    assert info.value.line == 2
    assert word in info.value.message

# 파일 읽기
def test_BOM_파일(tmp_path):
    path = tmp_path / "bom.usagi"
    path.write_text("미야아아\n야하핫\n", encoding="utf-8-sig")
    assert kinds(tokenize(read_source(path)))[0] == MAIN

def test_없는_파일():
    with pytest.raises(UsagiError):
        read_source("없는파일.usagi")


# 2단계

def test_2단계_키워드():
    tokens = tokenize("흐응 쥬르리 이야 핫")
    assert kinds(tokens) == [ASSIGN, INPUT_INT, ADD, MODULO, NEWLINE]

@pytest.mark.parametrize(
    "word, expected",
    [
        ("푸루", 1),
        ("푸루루", 2),
        ("푸루루루루루", 5),
    ],
)
def test_변수(word, expected):
    token = tokenize(word)[0]
    assert token.kind == VARIABLE
    assert token.value == expected

def test_대입문():
    tokens = tokenize("푸루 흐응 우라라 이야 우라")
    assert kinds(tokens) == [VARIABLE, ASSIGN, NUMBER, ADD, NUMBER, NEWLINE]

def test_붙여쓰면_나누기():
    tokens = tokenize("우라라라우라라")
    assert kinds(tokens) == [NUMBER, DIVIDE, NUMBER, NEWLINE]
    assert [t.value for t in tokens[:3]] == [3, None, 2]

def test_변수_붙여쓰기():
    tokens = tokenize("푸루루푸루 우라라라라우라")
    assert kinds(tokens) == [VARIABLE, DIVIDE, VARIABLE, NUMBER, DIVIDE, NUMBER, NEWLINE]
    assert [t.value for t in tokens[:3]] == [2, None, 1]

def test_세조각이상():
    tokens = tokenize("우라라라라우라라우라")
    assert kinds(tokens) == [NUMBER, DIVIDE, NUMBER, DIVIDE, NUMBER, NEWLINE]

def test_음수_0_붙여쓰기():
    tokens = tokenize("우루루루우우라라")
    assert [t.value for t in tokens if t.kind != NEWLINE] == [-3, None, 0, None, 2]
 
 
def test_공백_곱하기_붙여쓰면_나누기():
    assert kinds(tokenize("우라라라 우라라")) == [NUMBER, NUMBER, NEWLINE]
    assert kinds(tokenize("우라라라우라라")) == [NUMBER, DIVIDE, NUMBER, NEWLINE]
 
 
def test_키워드_잘림_검사():
    # 푸루야우라우라는 '우'를 포함하지만 키워드라서 붙여 쓴 단어로 자르지 않는다
    assert tokenize("미야아아\n푸루야우라우라 주석\n야하핫")[2].kind != DIVIDE

@pytest.mark.parametrize(
    "word",
    [
        "푸", # 루가 없는 변수
        "푸라", # 변수에 라
        "우라핫우라", # 핫을 붙여 씀
        "우라이야우라", # 이야를 붙여 씀
        "우라푸", # 마지막 조각이 푸
        "야하우라", # 키워드에 숫자를 붙임
    ],
)
def test_2단계_알수없는단어(word):
    with pytest.raises(UsagiError) as info:
        tokenize(f"미야아아\n야하 {word}")
    assert info.value.line == 2
    assert word in info.value.message

# 3단계

@pytest.mark.parametrize(
    "word, kind",
    [
        ("우나", EQUAL),
        ("우-라-", GREATER),
        ("-라-우", LESS),
        ("우-이-", NOT),
        ("하?", IF),
        ("하아?", ELSE),
        ("푸루야", WHILE),
        ("하아아앗!", BREAK),
        ("으핫!", CONTINUE),
    ],
)
def test_3단계_키워드(word, kind):
    assert kinds(tokenize(word)) == [kind, NEWLINE]


@pytest.mark.parametrize(
    "word, kind",
    [
        ("우ー라ー", GREATER),    # 일본어 장음 부호
        ("－라－우", LESS),       # 전각 하이픈
        ("우ー이ー", NOT),
        ("하？", IF),             # 전각 물음표
        ("하아？", ELSE),
        ("하아아앗！", BREAK),    # 전각 느낌표
        ("으핫！", CONTINUE),
    ],
)
def test_3단계_키워드_비슷한_기호(word, kind):
    assert kinds(tokenize(word)) == [kind, NEWLINE]


def test_전각_느낌표_정규화():
    assert normalize("하아아앗！") == "하아아앗!"


def test_우_푸로_시작하는_키워드는_정수_변수가_아님():
    # 우나, 우-라-, 우-이-는 '우'로, 푸루야는 '푸'로 시작하지만
    # 키워드 표를 먼저 확인하므로 정수·변수나 붙여 쓴 단어(나누기)로 읽지 않는다
    tokens = tokenize("푸루야 우-이- 푸루 우나 우 우-라- 우라")
    assert kinds(tokens) == [WHILE, NOT, VARIABLE, EQUAL, NUMBER, GREATER, NUMBER, NEWLINE]


def test_조건문_토큰():
    source = "미야아아\n하? 푸루 -라-우 우\n하아?\n야하핫\n야하핫"
    assert kinds(tokenize(source)) == [
        MAIN, NEWLINE,
        IF, VARIABLE, LESS, NUMBER, NEWLINE,
        ELSE, NEWLINE,
        BLOCK_END, NEWLINE,
        BLOCK_END, NEWLINE,
    ]


def test_반복문_토큰():
    source = "푸루야 우라\n하아아앗!\n으핫!\n야하핫"
    assert kinds(tokenize(source)) == [
        WHILE, NUMBER, NEWLINE,
        BREAK, NEWLINE,
        CONTINUE, NEWLINE,
        BLOCK_END, NEWLINE,
    ]


@pytest.mark.parametrize(
    "word",
    [
        "우라우나우라",   # 우나를 붙여 씀
        "우-라-우라",     # 우-라-에 숫자를 붙여 씀
        "-라-우우라",     # -라-우에 숫자를 붙여 씀
        "푸루야우라",     # 푸루야에 숫자를 붙여 씀
        "하",             # ?가 빠짐
        "하아앗!",        # 아가 하나 모자람
        "으핫",           # !가 빠짐
    ],
)
def test_3단계_알수없는단어(word):
    with pytest.raises(UsagiError) as info:
        tokenize(f"미야아아\n야하 {word}")
    assert info.value.line == 2
    assert word in info.value.message