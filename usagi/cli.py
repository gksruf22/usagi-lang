# usagi lang cli

import argparse
import sys

from usagi.errors import REACTION, UsagiError
from usagi.interpreter import run
from usagi.lexer import read_source, tokenize
from usagi.parser import parse

def build_arg_parser():
    arg_parser = argparse.ArgumentParser(
        prog="usagi",
        description="usagi lang interpreter",
    )
    arg_parser.add_argument("file", help="실행할 .usagi 파일")
    arg_parser.add_argument(
        "--unusagi",
        action="store_true",
        help="에러가 발생한 줄 번호와 설명을 보여준다.",
    )
    arg_parser.add_argument(
        "--tokens",
        action="store_true",
        help="실행하지 않고 lexer가 만든 토큰 목록만 보여준다.",
    )
    arg_parser.add_argument(
        "--ast",
        action="store_true",
        help="실행하지 않고 parser가 만든 AST만 보여준다",
    )
    return arg_parser

def setup_output():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    setup_output()

    try:
        source = read_source(args.file)
        tokens = tokenize(source)

        if args.tokens:
            for token in tokens:
                print(token)
            return 0

        program = parse(tokens)

        if args.ast:
            print(program)
            return 0

        run(program)

    except UsagiError as error:
        sys.stdout.flush()
        if args.unusagi:
            print(error.explain(), file=sys.stderr)
        else:
            print(REACTION, file=sys.stderr)
        return 1
    return 0