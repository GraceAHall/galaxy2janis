





class Test:
    def __init__(self):
        pass



class TestRegister:
    def __init__(self):
        self.tests: list[Test] = []

    def list(self) -> list[Test]:
        return self.tests
