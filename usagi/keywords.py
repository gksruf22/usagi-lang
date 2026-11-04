# usagi lang keywords

# 1. 토큰 종류 이름

MAIN = "MAIN" # 메인 블록 시작
BLOCK_END = "BLOCK_END" # 블록 끝
PRINT = "PRINT" # 숫자 출력(줄바꿈)
PRINT_NO_NEWLINE = "PRINT_NO_NEWLINE" # 숫자 출력
PRINT_CHAR = "PRINT_CHAR" # 글자 출력
NUMBER = "NUMBER" # 정수
NEWLINE = "NEWLINE" # 줄끝(lexer가 줄마다 넣음)

# 2. 키워드 철자

MAIN_WORD = "미야아아"
BLOCK_END_WORD = "야하핫"

# 3. 키워드 표

KEYWORDS = {
    MAIN_WORD: MAIN,
    BLOCK_END_WORD: BLOCK_END,
    "야하": PRINT,
    "야핫": PRINT_NO_NEWLINE,
    "루루루루루": PRINT_CHAR,
}

# 3. 주석 시작 글자

COMMENT_PREFIX = "푸루야우라우라"

# 4. 길이순 키워드 목록

KEYWORDS_BY_LENGTH = sorted(KEYWORDS, key=len, reverse=True)