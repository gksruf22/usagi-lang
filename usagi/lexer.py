# usagi lang lexer
# 소스코드를 토큰 목록으로 변경

import unicodedata
from dataclasses import dataclass

from usagi.errors import UsagiError
from usagi.keywords import (
    COMMENT_PREFIX,
    DIVIDE,
    KEYWORDS,
    NEGATIVE_UNIT,
    NEWLINE,
    NUMBER,
    NUMBER_HEAD,
    POSITIVE_UNIT,
    VARIABLE,
    VARIABLE_HEAD,
    VARIABLE_UNIT,
)


# 비슷하게 생긴 기호 통일
SYMBOL_REPLACEMENTS = {
    "ー": "-",   # 일본어 장음 부호
    "－": "-",   # 전각 하이픈
    "〜": "~",   # 물결 대시
    "～": "~",   # 전각 물결
    "∼": "~",   # 수학 물결
    "？": "?",   # 전각 물음표
}

@dataclass
class Token:
    kind: str # 토큰 종류 이름(keywords.py의 상수)
    value: object # 정수 토큰이면 그 숫자. 변수 토큰이면 변수 번호, 아니면 None
    line: int # 몇 번째 줄에서 나왔는지

def read_source(path):
    try:
        with open(path, encoding="utf-8-sig") as file:
            return file.read()
    except FileNotFoundError:
        raise UsagiError(f"파일을 찾을 수 없음: {path}")
    except UnicodeDecodeError:
        raise UsagiError(f"UTF-8로 읽을 수 없는 파일: {path}")


def normalize(line):
    line = unicodedata.normalize("NFC", line)
    for before, after in SYMBOL_REPLACEMENTS.items():
        line = line.replace(before, after)
    return line

def parse_number(word):
    if not word.startswith(NUMBER_HEAD):
        return None

    rest = word[len(NUMBER_HEAD):] # '우' 다음 글자들

    if rest == "":
        return 0
    if all(ch == POSITIVE_UNIT for ch in rest):
        return len(rest)
    if all(ch == NEGATIVE_UNIT for ch in rest):
        return -len(rest)
    return None

def parse_variable(word):
    if not word.startswith(VARIABLE_HEAD):
        return None

    rest = word[len(VARIABLE_HEAD):] # '푸' 다음 글자들

    if rest != "" and all(ch == VARIABLE_UNIT for ch in rest):
        return len(rest)
    return None

def split_pieces(word):
    pieces = []
    start = 0
    for i in range(1, len(word)):
        if word[i] in (NUMBER_HEAD, VARIABLE_HEAD):
            pieces.append(word[start:i])
            start = i
    pieces.append(word[start:])
    return pieces

def make_value_token(piece, line_number):
    number = parse_number(piece)
    if number is not None:
        return Token(NUMBER, number, line_number)

    index = parse_variable(piece)
    if index is not None:
        return Token(VARIABLE, index, line_number)

    return None

def make_tokens(word, line_number):
    # 키워드 표 확인
    if word in KEYWORDS:
        return [Token(KEYWORDS[word], None, line_number)]

    # 정수나 변수
    token = make_value_token(word, line_number)
    if token is not None:
        return [token]

    # 붙여 쓴 단어: 조각마다 정수/변수인지 확인, 조각 사이에 나누기
    pieces = split_pieces(word)
    if len(pieces) >= 2:
        tokens = []
        for i, piece in enumerate(pieces):
            token = make_value_token(piece, line_number)
            if token is None:
                break
            if i > 0:
                tokens.append(Token(DIVIDE, None, line_number))
            tokens.append(token)
        else:
            return tokens

    # 모두 아니면 알 수 없는 단어
    raise UsagiError(f"알 수 없는 단어: {word}", line_number)

def tokenize(source):
    tokens = []

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        # 1. 줄 앞뒤 공백/들여쓰기를 지우기
        line = raw_line.strip()

        # 2. 빈 줄 건너뛰기
        if line == "":
            continue

        # 3. 정규화
        line = normalize(line)

        # 4. 주석 건너뛰기
        if line.startswith(COMMENT_PREFIX):
            continue

        # 5. 공백 기준으로 나눠 단어 목록 만들기
        words = line.split()

        # 6. 단어마다 토큰 만들기
        for word in words:
            tokens.extend(make_tokens(word, line_number))

        # 7. 줄이 끝났다는 표시
        tokens.append(Token(NEWLINE, None, line_number))

    return tokens