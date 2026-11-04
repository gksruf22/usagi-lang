# usagi lang lexer
# 소스코드를 토큰 목록으로 변경

import unicodedata
from dataclasses import dataclass

from usagi.keywords import COMMENT_PREFIX, NEWLINE, KEYWORDS, NUMBER
from usagi.errors import UsagiError

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
    value: object # 정수 토큰이면 그 숫자. 아니면 None
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
    if not word.startswith("우"):
        return None

    rest = word[1:] # '우' 다음 글자들

    if rest == "":
        return 0
    if all(ch == "라" for ch in rest):
        return len(rest)
    if all(ch == "루" for ch in rest):
        return -len(rest)
    return None

def make_token(word, line_number):
    # 키워드 표 확인
    if word in KEYWORDS:
        return Token(KEYWORDS[word], None, line_number)
    
    # 키워드가 아니면 정수인지 확인
    number = parse_number(word)
    if number is not None:
        return Token(NUMBER, number, line_number)

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
            tokens.append(make_token(word, line_number))

        # 7. 줄이 끝났다는 표시
        tokens.append(Token(NEWLINE, None, line_number))

    return tokens