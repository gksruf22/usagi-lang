# interpreter test

import io

import pytest

from usagi.errors import UsagiError
from usagi.interpreter import run
from usagi.lexer import tokenize
from usagi.parser import parse
 
 
def run_source(source, input_text=""):
    """소스 코드를 렉서 → 파서 → 인터프리터에 차례로 출력된 글자를 반환."""
    out = io.StringIO()
    inp = io.StringIO(input_text)
    run(parse(tokenize(source)), out, inp)
    return out.getvalue()
 
 
def num(n):
    return "우" + "라" * n


# 숫자 출력

def test_빈_메인():
    assert run_source("미야아아\n야하핫") == ""

 
def test_숫자():
    source = (
        "미야아아\n"
        "  야하 우라라 우라라라\n"   # 2 × 3
        "  야하 우루 우라라라\n"     # -1 × 3
        "  야하 우\n"                # 0
        "  야핫 우라\n"              # 줄바꿈 없이 1
        "  야핫 우라라\n"            # 줄바꿈 없이 2
        "야하핫"
    )
    assert run_source(source) == "6\n-3\n0\n12"
 
 
def test_음수끼리_곱():
    assert run_source("미야아아\n야하 우루루 우루루루\n야하핫") == "6\n"


# 문자 출력
def test_Hi_출력():
    source = (
        "미야아아\n"
        f"  루루루루루 {num(8)} {num(9)}\n"            # H = 72
        f"  루루루루루 {num(3)} {num(5)} {num(7)}\n"   # i = 105
        f"  루루루루루 {num(2)} {num(5)}\n"            # 줄바꿈 = 10
        "야하핫"
    )
    assert run_source(source) == "Hi\n"
 
 
def test_한글_출력():
    source = f"미야아아\n루루루루루 {num(32)} {num(32)} {num(43)}\n야하핫"
    assert run_source(source) == "가"

# 에러
@pytest.mark.parametrize(
    "expr, code",
    [
        ("우", 0), # 0은 쓸 수 없음
        ("우루", -1), # 음수
        (f"{num(216)} {num(256)}", 55296), # 0xD800 (서로게이트 시작)
        (f"{num(1024)} {num(1088)}", 1114112), # 0x110000 (유니코드 범위 밖)
    ],
)
def test_잘못된_문자_코드는_에러(expr, code):
    with pytest.raises(UsagiError) as info:
        run_source(f"미야아아\n야하 우라\n루루루루루 {expr}\n야하핫")
    assert info.value.line == 3
    assert info.value.message == f"출력할 수 없는 문자 코드: {code}"


# 2단계
def main(*lines):
    return "미야아아\n" + "\n".join(lines) + "\n야하핫"

def test_변수_대입_읽기():
        source = main(
            "푸루 흐응 우라라라", # 푸루 = 3
            "푸루루 흐응 푸루 우라라", # 푸루루 = 3 × 2 = 6
            "야하 푸루루",
            "푸루루 흐응 푸루루 이야 우루 푸루", # 푸루루 = 6 - 3 = 3
            "야하 푸루루",
            "야하 푸루루푸루", # 3 / 3 = 1
        )
        assert run_source(source) == "6\n3\n1\n"

@pytest.mark.parametrize(
    "expr, expected",
    [
        ("우라 이야 우라라 우라라라", 7), # 1 + 2 × 3
        ("우라라라 우라라라라라우라라 이야 우라", 8), # (3 × 5) / 2 + 1
        ("우라라라라라 이야 우루 우라라", 3), # 5 - 2
        ("우라라라라라라라 핫 우라라라", 1), # 7 % 3
        ("우라라라라라라라우라라", 3), # 7 / 2
        ("우루루루루루루루우라라", -3), # -7 / 2 (0 쪽으로 버림)
        ("우루루루루루루루 핫 우라라", -1), # -7 % 2 (왼쪽 수의 부호)
        ("우라라라라라라라우루루", -3), # 7 / -2
        ("우라라라라라라라 핫 우루루", 1), # 7 % -2
        ("우라라라라라라라라우라라우라라", 2), # (8 / 2) / 2
    ],
)

def test_연산(expr, expected):
    assert run_source(main(f"야하 {expr}")) == f"{expected}\n"

def test_계산기():
    source = main("쥬르리 푸루", "쥬르리 푸루루", "야하 푸루 이야 푸루루")
    assert run_source(source, "3\n4\n") == "7\n"

def test_입력은_앞뒤공백_음수허용():
    assert run_source(main("쥬르리 푸루", "야하 푸루"), "  -42  \n") == "-42\n"

@pytest.mark.parametrize(
    "source, input_text, line, message",
    [
        (main("야하 푸루루"), "", 2, "아직 값을 넣지 않은 변수: 푸루루"),
        (main("야하 우라우"), "", 2, "0으로 나눌 수 없음"),
        (main("야하 우라 핫 우"), "", 2, "0으로 나눌 수 없음"),
        (main("푸루 흐응 우", "야하 우라푸루"), "", 3, "0으로 나눌 수 없음"),
        (main("쥬르리 푸루"), "", 2, "더 읽을 입력이 없음"),
        (main("쥬르리 푸루"), "abc\n", 2, "정수 입력에 숫자가 아닌 값: abc"),
        (main("쥬르리 푸루"), "3.5\n", 2, "정수 입력에 숫자가 아닌 값: 3.5"),
        (main("쥬르리 푸루"), "우라라\n", 2, "정수 입력에 숫자가 아닌 값: 우라라"),
    ],
)
def test_2단계_실행에러(source, input_text, line, message):
    with pytest.raises(UsagiError) as info:
        run_source(source, input_text)
    assert info.value.line == line
    assert info.value.message == message

# 3단계

# 비교와 NOT

@pytest.mark.parametrize(
    "expr, expected",
    [
        ("우라 우나 우라", 1),             # 1 == 1
        ("우라 우나 우라라", 0),           # 1 == 2
        ("우라라 우-라- 우라", 1),         # 2 > 1
        ("우라 우-라- 우라", 0),           # 1 > 1
        ("우라 -라-우 우라라", 1),         # 1 < 2
        ("우라라 -라-우 우라", 0),         # 2 < 1
        ("우루 -라-우 우", 1),             # -1 < 0
        ("우라 이야 우라 우나 우라라", 1), # (1 + 1) == 2
        ("우라 우나 우라 우나 우라", 1),   # (1 == 1) == 1
        ("우-이- 우", 1),                  # NOT 0
        ("우-이- 우라라라", 0),            # NOT 3 (0이 아니면 참)
        ("우-이- 우라 우나 우라", 0),      # NOT (1 == 1)
        ("우-이- 우-이- 우라라라", 1),     # NOT NOT 3
    ],
)
def test_비교와_NOT(expr, expected):
    assert run_source(main(f"야하 {expr}")) == f"{expected}\n"


def test_그리고는_변수에_담아_곱하기():
    # 푸루 > 0 그리고 푸루 < 3
    lines = [
        "쥬르리 푸루",
        "푸루루 흐응 푸루 우-라- 우",
        "푸루루루 흐응 푸루 -라-우 우라라라",
        "야하 푸루루 푸루루루",
    ]
    assert run_source(main(*lines), "2\n") == "1\n"
    assert run_source(main(*lines), "5\n") == "0\n"


# 조건문

@pytest.mark.parametrize(
    "condition, expected",
    [
        ("우라", "1\n"),    # 참이면 하? 아래
        ("우", "2\n"),      # 거짓이면 하아? 아래
        ("우루", "1\n"),    # 음수도 0이 아니므로 참
    ],
)
def test_조건문_아니면(condition, expected):
    source = main(
        f"하? {condition}",
        "야하 우라",
        "하아?",
        "야하 우라라",
        "야하핫",
    )
    assert run_source(source) == expected


def test_조건문_거짓이고_아니면_없음():
    source = main("하? 우", "야하 우라", "야하핫", "야하 우라라")
    assert run_source(source) == "2\n"


@pytest.mark.parametrize(
    "number, expected",
    [
        ("1", "1\n"),
        ("2", "2\n"),
        ("7", "0\n"),
    ],
)
def test_아니면_만약(number, expected):
    source = main(
        "쥬르리 푸루",
        "하? 푸루 우나 우라",
        "야하 우라",
        "하아?",
        "하? 푸루 우나 우라라",
        "야하 우라라",
        "하아?",
        "야하 우",
        "야하핫",
        "야하핫",
    )
    assert run_source(source, f"{number}\n") == expected


# 반복문

def test_반복문_1부터_5까지():
    source = main(
        "푸루 흐응 우라",
        "푸루야 우-이- 푸루 우-라- 우라라라라라",
        "야하 푸루",
        "푸루 흐응 푸루 이야 우라",
        "야하핫",
    )
    assert run_source(source) == "1\n2\n3\n4\n5\n"


def test_반복문_조건이_처음부터_거짓():
    source = main("푸루야 우", "야하 우라", "야하핫", "야하 우라라")
    assert run_source(source) == "2\n"


def test_반복문_합계():
    # 1 + 2 + … + 10 = 55
    source = main(
        "푸루 흐응 우라",
        "푸루루 흐응 우",
        "푸루야 우-이- 푸루 우-라- 우라라라라라라라라라라",
        "푸루루 흐응 푸루루 이야 푸루",
        "푸루 흐응 푸루 이야 우라",
        "야하핫",
        "야하 푸루루",
    )
    assert run_source(source) == "55\n"


def test_탈출과_건너뛰기():
    # 10보다 작은 홀수
    source = main(
        "푸루 흐응 우",
        "푸루야 우라",
        "푸루 흐응 푸루 이야 우라",
        "하? 푸루 우-라- 우라라라라라라라라라",
        "하아아앗!",
        "야하핫",
        "하? 푸루 핫 우라라 우나 우",
        "으핫!",
        "야하핫",
        "야하 푸루",
        "야하핫",
    )
    assert run_source(source) == "1\n3\n5\n7\n9\n"


def test_탈출은_가장_가까운_반복문만():
    # 안쪽 반복문에서 하아아앗!을 해도 바깥 반복문은 계속된다
    # 줄마다 (푸루 × 10 + 푸루루)를 출력하는데, 푸루루가 2가 되면 안쪽 반복만 끝난다
    source = main(
        "푸루 흐응 우라",
        f"푸루야 우-이- 푸루 우-라- {num(3)}",
        "푸루루 흐응 우라",
        "푸루야 우라",
        f"야핫 푸루 {num(10)} 이야 푸루루",
        f"루루루루루 {num(32)}",                # 공백
        f"하? 푸루루 우나 {num(2)}",
        "하아아앗!",
        "야하핫",
        "푸루루 흐응 푸루루 이야 우라",
        "야하핫",
        f"루루루루루 {num(2)} {num(5)}",        # 줄바꿈
        "푸루 흐응 푸루 이야 우라",
        "야하핫",
    )
    assert run_source(source) == "11 12 \n21 22 \n31 32 \n"


def test_입력이_0일_때까지_더하기():
    source = main(
        "푸루루 흐응 우",
        "쥬르리 푸루",
        "푸루야 푸루",
        "푸루루 흐응 푸루루 이야 푸루",
        "쥬르리 푸루",
        "야하핫",
        "야하 푸루루",
    )
    assert run_source(source, "3\n4\n5\n0\n") == "12\n"


def test_반복문_안의_에러_줄번호():
    # 푸루가 2 → 1 → 0으로 줄어들다가, 0이 된 차례에 5번째 줄에서 0으로 나누기
    source = main(
        "푸루 흐응 우라라",              # 2번째 줄
        "푸루야 우라",                    # 3번째 줄
        "푸루 흐응 푸루 이야 우루",       # 4번째 줄: 푸루 - 1
        "야하 우라푸루",                  # 5번째 줄: 1 / 푸루
        "야하핫",
    )
    with pytest.raises(UsagiError) as info:
        run_source(source)
    assert info.value.line == 5
    assert info.value.message == "0으로 나눌 수 없음"
