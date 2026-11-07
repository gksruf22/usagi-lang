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
 