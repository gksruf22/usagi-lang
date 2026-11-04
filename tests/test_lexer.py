# lexer test

import unicodedata

import pytest

from usagi.errors import UsagiError
from usagi.keywords import (
    BLOCK_END,
    MAIN,
    NEWLINE,
    NUMBER,
    PRINT,
    PRINT_CHAR,
    PRINT_NO_NEWLINE,
)
from usagi.lexer import read_source, tokenize

def kinds(tokens):
    return [token.kind for token in tokens]

# 키워드
def test_키워드():
    tokens = tokenize("미야아아\n야하\n야핫\n루루루루루\n후으-응")
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
    source = "미야아아\n\n푸루야우라우라 설명 \n야하 우라\n후으-응"
    tokens = tokenize(source)
    assert kinds(tokens) == [MAIN, NEWLINE, PRINT, NUMBER, NEWLINE, BLOCK_END, NEWLINE]
    assert [t.line for t in tokens if t.kind == NEWLINE] == [1, 4, 5]

def test_들여쓰기_탭_공백여러칸():
    tokens = tokenize("\t  야하   우라\t\t우라라  ")
    assert kinds(tokens) == [PRINT, NUMBER, NUMBER, NEWLINE]

# 정규화
def test_하이픈():
    assert tokenize("후으ー응")[0].kind == BLOCK_END

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
    path.write_text("미야아아\n후으-응\n", encoding="utf-8-sig")
    assert kinds(tokenize(read_source(path)))[0] == MAIN

def test_없는_파일():
    with pytest.raises(UsagiError):
        read_source("없는파일.usagi")
