# usagi lang keywords

# 1. 토큰 종류 이름

# 1단계
MAIN = "MAIN" # 메인 블록 시작
BLOCK_END = "BLOCK_END" # 블록 끝
PRINT = "PRINT" # 숫자 출력(줄바꿈)
PRINT_NO_NEWLINE = "PRINT_NO_NEWLINE" # 숫자 출력
PRINT_CHAR = "PRINT_CHAR" # 글자 출력
NUMBER = "NUMBER" # 정수
NEWLINE = "NEWLINE" # 줄끝(lexer가 줄마다 넣음)

# 2단계
VARIABLE = "VARIABLE" # 변수
ASSIGN = "ASSIGN" # 대입
INPUT_INT = "INPUT_INT" # 정수 입력
ADD = "ADD" # 더하기
MODULO = "MODULO" # 나머지
DIVIDE = "DIVIDE" # 나누기(키워드가 아니라 lexer가 붙여 쓴 단어를 자른 자리에 넣음)

# 2. 키워드 철자

MAIN_WORD = "미야아아"
BLOCK_END_WORD = "야하핫"
ASSIGN_WORD = "흐응"
INPUT_INT_WORD = "쥬르리"

# 3. 키워드 표

KEYWORDS = {
    MAIN_WORD: MAIN,
    BLOCK_END_WORD: BLOCK_END,
    "야하": PRINT,
    "야핫": PRINT_NO_NEWLINE,
    "루루루루루": PRINT_CHAR,
    ASSIGN_WORD: ASSIGN,
    INPUT_INT_WORD: INPUT_INT,
    "이야": ADD,
    "핫": MODULO,
}

# 4. 정수와 변수를 만드는 글자(lexer가 글자 수를 셀 때 쓴다)

NUMBER_HEAD = "우" # 정수 첫 글자
POSITIVE_UNIT = "라" # 개수만큼 +1
NEGATIVE_UNIT = "루" # 개수만큼 -1
VARIABLE_HEAD = "푸" # 변수 첫 글자
VARIABLE_UNIT = "루" # 개수 = 변수 번호

# 5. 주석 시작 글자

COMMENT_PREFIX = "푸루야우라우라"

# 6. 길이순 키워드 목록

KEYWORDS_BY_LENGTH = sorted(KEYWORDS, key=len, reverse=True)