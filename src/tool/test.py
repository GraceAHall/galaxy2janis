





from dataclasses import dataclass

from tool.param.InputParam import InputParam
from tool.param.OutputParam import OutputParam


class Test:
    def __init__(self):
        pass

@dataclass
class TestInput:
    output: InputParam
    value: str


@dataclass
class TestOutput:
    output: OutputParam
    compare_file: str


class TestRegister:
    def __init__(self, incoming: list[Test]):
        self.tests: list[Test] = []
        for test in incoming:
            self.add(test)

    def list(self) -> list[Test]:
        return self.tests

    def add(self, test: Test) -> None:
        self.tests.append(test)