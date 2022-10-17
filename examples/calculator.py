import nodeflow as nf


class Constant(nf.Operator):
    def __init__(self, value:int, name: str=None):
        super().__init__(name)
        self.value = value

    def evaluate(self)->int:
        return self.value


class Increment(nf.Operator):
    def __init__(self, input: nf.Operator, name:str=None):
        super().__init__(name=name)
        self.input = input

    def evaluate(self, x):
        return x+1


class Plus(nf.Operator):
    def __init__(self, A: nf.Operator, B:nf.Operator, name: str=None):
        super().__init__(name)
        self.A = A
        self.B = B

    def evaluate(self, a:int, b: int)->int:
        return a+b


class Subtract(nf.Operator):
    def __init__(self, A:nf.Operator, B:nf.Operator, name: str=None):
        super().__init__(name)
        self.A = A
        self.B = B

    def evaluate(self, a:int, b:int)->int:
        return a-b


class Multiply(nf.Operator):
    def __init__(self, A:nf.Operator, B:nf.Operator, name: str=None):
        super().__init__(name)
        self.A = A
        self.B = B

    def evaluate(self, a:int, b:int)->int:
        return a*b


class Divide(nf.Operator):
    def __init__(self, A:nf.Operator, B:nf.Operator, name: str=None):
        super().__init__(name)
        self.A = A
        self.B = B

    def evaluate(self, a:int, b:int)->int:
        return a/b

from typing import Any

class Cache(nf.Operator):
    """conditional evaluation source"""
    def __init__(self, key:nf.Operator, source:nf.Operator):
        self.key = key
        self.source = source
        self.cache = dict()

    def sources(self):
        if hash(self.source) != self.source_hash:
            return [self.source]
        else:
            return []

    def evaluate(self, key, value: Any=None):
        if key not in cache:

        if value is not None:
            self.cache = value
            self.source_hash = hash(self.source)
        
        return self.cache

if __name__ == "__main__":
    one = Constant(1, name="one")
    two = Constant(2, name="two")
    plus1 = Plus(one, two, name="plus1")
    plus2 = Plus(plus1, plus1, name="plus2")

    result = nf.evaluate(plus2, verbose=True)

    print(result)

    import pythonflow as pf
