# example test

import io
from pathlib import Path

import pytest

from usagi.interpreter import run
from usagi.lexer import read_source, tokenize
from usagi.parser import parse

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.rglob("*.usagi"))
 
 
def test_예제_하나_이상():
    assert EXAMPLES, "examples/ 폴더에 .usagi 파일이 없음"
 
 
@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.relative_to(EXAMPLES_DIR).with_suffix("").as_posix(),)
def test_예제_출력(example):
    expected_file = example.with_suffix(".out")
    assert expected_file.exists(), f"{expected_file.name} 파일이 없음 (기대 출력을 만들어 주세요)"

    input_file = example.with_suffix(".in")
    if input_file.exists():
        input_text = input_file.read_text(encoding="utf-8")
    else:
        input_text = ""

    out = io.StringIO()
    inp = io.StringIO(input_text)
    run(parse(tokenize(read_source(example))), out, inp)
 
    expected = expected_file.read_text(encoding="utf-8")
    assert out.getvalue() == expected
 