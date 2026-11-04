# usagi lang parser

from usagi.errors import UsagiError
from usagi.keywords import (
    BLOCK_END,
    BLOCK_END_WORD,
    MAIN,
    MAIN_WORD,
    NEWLINE,
    NUMBER,
    PRINT,
    PRINT_CHAR,
    PRINT_NO_NEWLINE,
)
from usagi.nodes import (
    Function,
    Multiply,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Program,
)

def parse(tokens):
    return Parser(tokens).parse_program()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens # 렉서가 만든 토큰 목록
        self.pos = 0 # 지금 보고 있는 토큰의 위치


    # 기본 도구

    def peek(self): # 현재 토큰 확인
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self): # 토큰을 가져가고 위치를 한 칸 옮김
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, kind, message, line): # 지금 토큰이 kind 면 먹고, 아니면 에러.
        token = self.peek()
        if token is None or token.kind != kind:
            raise UsagiError(message, line)
        return self.advance()


    # 문법 규칙

    def parse_program(self):
        """프로그램 = 메인블록"""

        # 미야아아가 없는 경우
        if not any(token.kind == MAIN for token in self.tokens):
            raise UsagiError(f"메인 블록({MAIN_WORD})이 없음")

        # 메인 블록 앞에 다른 문장이 있는 경우
        first = self.peek()
        if first.kind != MAIN:
            raise UsagiError("메인 블록 밖에 문장이 있음", first.line)

        main = self.parse_main()

        # 메인 블록 뒤에 토큰이 남아 있는 경우
        rest = self.peek()
        if rest is not None:
            if rest.kind == MAIN:
                raise UsagiError("메인 블록이 두 개 있음", rest.line)
            raise UsagiError("메인 블록 밖에 문장이 있음", rest.line)

        return Program(main)

    def parse_main(self):
        """메인블록 = "미야아아" , 줄끝 , { 문장 , 줄끝 } , "야하핫" , [ 줄끝 ]"""
        start = self.advance()
        self.expect(NEWLINE, f"메인 시작({MAIN_WORD}) 뒤에 다른 단어가 있음", start.line)
        body = self.parse_block(start)
        return Function("main", 0, body, start.line)

    def parse_block(self, opener):
        statements = []

        while True:
            token = self.peek()

            # 블록 끝 전에 토큰이 다 떨어진 경우
            if token is None:
                raise UsagiError(f"블록 끝({BLOCK_END_WORD})이 없음", opener.line)

            # 블록 끝
            if token.kind == BLOCK_END:
                self.advance()
                self.expect(NEWLINE, f"블록 끝({BLOCK_END_WORD}) 뒤에 다른 단어가 있음", token.line)
                return statements

            statements.append(self.parse_statement())

    def parse_statement(self):
        token = self.advance()

        if token.kind == PRINT:
            node = Print(self.parse_expression(token), token.line)
        elif token.kind == PRINT_NO_NEWLINE:
            node = PrintNoNewline(self.parse_expression(token), token.line)
        elif token.kind == PRINT_CHAR:
            node = PrintChar(self.parse_expression(token), token.line)
        else:
            raise UsagiError("문장을 시작할 수 없는 단어", token.line)

        # 문장이 끝나면 반드시 줄이 끝나야 함
        self.expect(NEWLINE, "한 줄에 문장은 하나만 쓸 수 있음", token.line)
        return node

    def parse_expression(self, owner):
        token = self.peek()
        if token is None or token.kind != NUMBER:
            raise UsagiError("출력할 값이 없음", owner.line)

        self.advance()
        node = Number(token.value, token.line)

        # 다음 토큰도 정수면 곱셈
        while self.peek() is not None and self.peek().kind == NUMBER:
            right = self.advance()
            node = Multiply(node, Number(right.value, right.line), right.line)

        return node
