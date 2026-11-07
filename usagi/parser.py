# usagi lang parser

from usagi.errors import UsagiError
from usagi.keywords import (
    ADD,
    ASSIGN,
    BLOCK_END,
    BLOCK_END_WORD,
    DIVIDE,
    INPUT_INT,
    MAIN,
    MAIN_WORD,
    MODULO,
    NEWLINE,
    NUMBER,
    PRINT,
    PRINT_CHAR,
    PRINT_NO_NEWLINE,
    VARIABLE,
)
from usagi.nodes import (
    Add,
    Assign,
    Divide,
    Function,
    InputInt,
    Modulo,
    Multiply,
    Number,
    Print,
    PrintChar,
    PrintNoNewline,
    Program,
    Variable,
)

VALUE_KINDS = (NUMBER, VARIABLE)

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

    def peek_kind(self): # 현재 토큰의 종류. 토큰이 없으면 None
        token = self.peek()
        return token.kind if token is not None else None

    def advance(self): # 토큰을 가져가고 위치를 한 칸 옮김
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, kind, message, line): # 지금 토큰이 kind 면 먹고, 아니면 에러.
        token = self.peek()
        if token is None or token.kind != kind:
            raise UsagiError(message, line)
        return self.advance()


    # 문법 규칙: 프로그램, 블록

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


    # 문법 규칙: 문장

    def parse_statement(self):
        token = self.advance()

        if token.kind == PRINT:
            node = Print(self.parse_expression(token, "출력할 값이 없음"), token.line)
        elif token.kind == PRINT_NO_NEWLINE:
            node = PrintNoNewline(self.parse_expression(token, "출력할 값이 없음"), token.line)
        elif token.kind == PRINT_CHAR:
            node = PrintChar(self.parse_expression(token, "출력할 값이 없음"), token.line)
        elif token.kind == VARIABLE:
            node = self.parse_assign(token)
        elif token.kind == INPUT_INT:
            node = self.parse_input_int(token)
        else:
            raise UsagiError("문장을 시작할 수 없는 단어", token.line)

        # 문장이 끝나면 반드시 줄이 끝나야 함
        self.expect(NEWLINE, "한 줄에 문장은 하나만 쓸 수 있음", token.line)
        return node

    def parse_assign(self, target):
        next_kind = self.peek_kind()

        # 왼쪽 변수 하나가 아닌 경우
        if next_kind == DIVIDE:
            raise UsagiError("값을 넣을 곳은 변수 하나여야 함", target.line)

        # 변수로 시작했는데 흐응이 없는 경우
        if next_kind != ASSIGN:
            raise UsagiError("문장을 시작할 수 없는 단어", target.line)

        self.advance()
        expr = self.parse_expression(target, "넣을 값이 없음")
        return Assign(target.value, expr, target.line)

    def parse_input_int(self, keyword):
        message = "입력을 넣을 곳은 변수 하나여야 함"
        target = self.expect(VARIABLE, message, keyword.line)

        # 변수 뒤에 나누기가 붙은 경우
        if self.peek_kind() == DIVIDE:
            raise UsagiError(message, keyword.line)

        return InputInt(target.value, keyword.line)


    # 문법 규칙: 식(계산 순서: 항을 먼저 묶고 더하기는 나중)
    def parse_expression(self, owner, missing_message):
        node = self.parse_term(owner, missing_message)

        # 이야가 나오면 오른쪽 항을 읽어 더하기로 묶는다. 왼쪽부터 차례로 묶인다.
        while self.peek_kind() == ADD:
            operator = self.advance()
            right = self.parse_term(operator, "계산할 값이 없음")
            node = Add(node, right, operator.line)

        return node

    def parse_term(self, owner, missing_message):
        node = self.parse_value(owner, missing_message)

        while True:
            kind = self.peek_kind()

            if kind in VALUE_KINDS:
                right = self.parse_value(owner, missing_message)
                node = Multiply(node, right, right.line)

            elif kind == DIVIDE:
                operator = self.advance()
                right = self.parse_value(operator, "계산할 값이 없음")
                node = Divide(node, right, operator.line)
 
            elif kind == MODULO:
                operator = self.advance()
                right = self.parse_value(operator, "계산할 값이 없음")
                node = Modulo(node, right, operator.line)

            else:
                return node

    def parse_value(self, owner, missing_message):
        token = self.peek()

        if token is not None and token.kind == NUMBER:
            self.advance()
            return Number(token.value, token.line)
 
        if token is not None and token.kind == VARIABLE:
            self.advance()
            return Variable(token.value, token.line)
 
        raise UsagiError(missing_message, owner.line)