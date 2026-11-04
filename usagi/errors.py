# usagi lang 에러

# 기본: 하아?
# --unusagie: [3번째 줄] 알 수 없는 단어: 우라루

REACTION = "하아?" # 모든 에러에서 출력하는 말

class UsagiError(Exception):
    """
    message: --unusagi 일 때 보여줄 자연어 설명
    line: 에러가 발생한 줄 번호
    """
    def __init__(self, message, line=None):
        super().__init__(message)
        self.message = message
        self.line = line

    def explain(self):
        # --unusagi에서 보여줄 설명
        if self.line is None:
            return self.message
        return f"[{self.line}번째 줄] {self.message}"