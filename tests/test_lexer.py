# lexer test

import unicodedata

import pytest

from usagi.errors import UsagiError
from usagi.keywords import (
    ADD,
    ASSIGN,
    BLOCK_END,
    DIVIDE,
    INPUT_INT,
    MAIN,
    MODULO,
    NEWLINE,
    NUMBER,
    PRINT,
    PRINT_CHAR,
    PRINT_NO_NEWLINE,
    VARIABLE,
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
        "우-라-", # 1단계에 없는 키워드
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
 