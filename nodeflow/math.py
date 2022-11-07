from typing import Callable, Any, Hashable, Union
from nodeflow.core import Operator, Constant, operator


class Plus(Operator):
    def __init__(self, A:Operator, B:Operator):
        super().__init__(A, B)

    def __call__(self, a:Union[int, float], b:Union[int, float]):
        return a+b


class Minus(Operator):
    def __init__(self, A:Operator, B:Operator):
        super().__init__(A, B)

    def __call__(self, a:Union[int, float], b:Union[int, float]):
        return a-b


class Multiply(Operator):
    def __init__(self, A:Operator, B:Operator):
        super().__init__(A, B)

    def __call__(self, a:Union[int, float], b:Union[int, float]):
        return a*b


class Divide(Operator):
    def __init__(self, A:Operator, B:Operator):
        super().__init__(A, B)

    def __call__(self, a:Union[int, float], b:Union[int, float]):
        return a/b


if __name__ == "__main__":

    one = Constant(1, name="one")
    five = Constant(5, name="five")
    plus = Plus(one, five)
    minus = Minus(five, one)
    divide = Divide(plus,five)
    mult = Multiply(divide, one)

    
    result = mult.evaluate(verbose=True)
    print(result)
