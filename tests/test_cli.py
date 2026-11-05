# cli test

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def usagi(*args):
    """python -m usagi <args>"""
    return subprocess.run(
        [sys.executable, "-m", "usagi", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

def write_source(tmp_path, source):
    path = tmp_path / "test.usagi"
    path.write_text(source, encoding="utf-8")
    return str(path)

# 정상 실행
def test_실행(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하 우라라 우라라라\n야하핫\n")
    result = usagi(path)
    assert result.stdout == "6\n"
    assert result.stderr == ""
    assert result.returncode == 0

def test_tokens_옵션(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하핫\n")
    result = usagi("--tokens", path)
    assert "Token(kind='MAIN'" in result.stdout
    assert result.returncode == 0

def test_ast_옵션(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하 우라\n야하핫\n")
    result = usagi("--ast", path)
    assert result.stdout.startswith("Program(")
    assert "Print(" in result.stdout
    assert result.returncode == 0

# 에러
def test_에러_하아(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하 우라루\n야하핫\n")
    result = usagi(path)
    assert result.stderr == "하아?\n"
    assert result.returncode == 1
    assert "Traceback" not in result.stdout

def test_unusagi(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하 우라루\n야하핫\n")
    result = usagi("--unusagi", path)
    assert result.stderr == "[2번째 줄] 알 수 없는 단어: 우라루\n"
    assert result.returncode == 1

def test_없는파일(tmp_path):
    result = usagi("--unusagi", "없는파일.usagi")
    assert result.stderr == "파일을 찾을 수 없음: 없는파일.usagi\n"
    assert result.returncode == 1

def test_에러전_출력결과(tmp_path):
    path = write_source(tmp_path, "미야아아\n야하 우라\n루루루루루 우\n야하핫\n")
    result = usagi(path)
    assert result.stdout == "1\n"
    assert result.stderr == "하아?\n"
    assert result.returncode == 1