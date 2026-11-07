# usagi lang variable storage

from usagi.errors import UsagiError
from usagi.keywords import VARIABLE_HEAD, VARIABLE_UNIT

def variable_name(index):
    return VARIABLE_HEAD + VARIABLE_UNIT * index

class Environment:
    def __init__(self):
        self.values = {}

    def get(self, index, line):
        if index not in self.values:
            raise UsagiError(f"아직 값을 넣지 않은 변수: {variable_name(index)}", line)
        return self.values[index]

    def set(self, index, value):
        self.values[index] = value