from typing import Callable, Any, Hashable
from core import Operator


class Constant(Operator):
    def __init__(self, value:Any, name: str=None):
        super().__init__(name)
        self.value = value

    def __call__(self)->Any:
        return self.value


def operator(f: Callable):
    class Op(Operator):
        def __init__(self, *args):
            super().__init__(name=f.__name__)
            self.inputs = args

        def dependencies(self):
            return self.inputs

        def __call__(self, *args):
            print("evaluate: ", args)
            return f(*args)

    return Op


@operator
def Plus(a:int, b:int):
    return a+b

@operator
def Minus(a:int, b:int):
    return a-b

@operator
def Multiply(a:int, b:int):
    return a*b

@operator
def Divide(a:int, b:int):
    return a/b

if __name__ == "__main__":

    from core import evaluate
    one = Constant(1)
    five = Constant(5)
    plus = Plus(one, five)
    minus = Minus(five, one)
    divide = Divide(plus,five)

    result = evaluate(divide, verbose=True)

    print(result)
