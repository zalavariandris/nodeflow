import unittest
from nodeflow import Operator, Constant, Variable, Cache, operator

class Add(Operator):
    def __init__(self, A=Constant(0), B=Constant(0)):
        super().__init__(A, B)

    def __call__(self, a, b):
        return a+b


class OperatorCreation(unittest.TestCase):
    """cerate operators, and evaluate graph with single node"""
    def test_constant(self):
        five = Constant(5)
        self.assertEqual( five.evaluate(), 5 )

    def test_variable(self):
        x = Variable(1)
        self.assertEqual(x.evaluate(), 1)
        x.value = 2
        self.assertEqual(x.evaluate(), 2)

    def test_custom_operator_class(self):
        add = Add(Constant(1), Constant(2))
        self.assertEqual(add.evaluate(), 3)

    def test_operator_from_function(self):
        def f(a, b):
            return a+b

        Add = operator(f)
        three = Add(Constant(1), Constant(2))
        self.assertEqual(f(1,2), three.evaluate())


class ReconnectInputs(unittest.TestCase):
    def test_setting_inputs(self):
        one = Constant(1)
        two = Constant(2)
        three = Constant(3)
        four = Constant(4)
        five = Constant(5)

        add = Add()

        add.set_inputs(one, two)
        self.assertEqual(add.evaluate(), 3)

        add.set_inputs(one, three)
        self.assertEqual(add.evaluate(), 4)

        add.set_inputs(A=four, B=five)
        self.assertEqual(add.evaluate(), 9)


class CacheOperator(unittest.TestCase):
    def test_request(self):
        import requests
        
        # create the graph
        url = "https://github.com/zalavariandris/nodeflow"
        Request = operator(lambda url: requests.get(url).text)
        request = Request(Constant(url))

        # evaluate the graph
        result = request.evaluate()

        # test against raw requests lib
        self.assertTrue(requests.get(url).text, result)
        self.assertTrue(result.strip().startswith("<!DOCTYPE html>"))


if __name__ == '__main__':
    unittest.main(verbosity=2)