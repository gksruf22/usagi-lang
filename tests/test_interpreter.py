# interpreter test

import io

import pytest

from usagi.errors import UsagiError
from usagi.interpreter import run
from usagi.lexer import tokenize
from usagi.parser import parse
 
 
def run_source(source):
    """소스 코드를 렉서 → 파서 → 인터프리터에 차례로 출력된 글자를 반환."""
    out = io.StringIO()
    run(parse(tokenize(source)), out)
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
        ("우", 0),                          # 0은 쓸 수 없음
        ("우루", -1),                       # 음수
        (f"{num(216)} {num(256)}", 55296),  # 0xD800 (서로게이트 시작)
        (f"{num(1024)} {num(1088)}", 1114112),  # 0x110000 (유니코드 범위 밖)
    ],
)
def test_잘못된_문자_코드는_에러(expr, code):
    with pytest.raises(UsagiError) as info:
        run_source(f"미야아아\n야하 우라\n루루루루루 {expr}\n야하핫")
    assert info.value.line == 3
    assert info.value.message == f"출력할 수 없는 문자 코드: {code}"