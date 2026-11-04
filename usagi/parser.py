# usagi lang parser

from usagi.errors import UsagiError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens # 렉서가 만든 토큰 목록
        self.pos = 0 # 지금 보고 있는 토큰의 위치

    # 기본 도구

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, kind, message, line):
        token = self.peek()
        if token is None or token.kind != kind:
            raise UsagiError(message, line)
        return self.advance()