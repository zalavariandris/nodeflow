import unittest
from nodeflow import Operator, Constant, Variable, Cache, evaluate, operator

class Add(Operator):
    def __init__(self, A, B):
        super().__init__(A, B)

    def __call__(self, a, b):
        return a+b


class OperatorCreation(unittest.TestCase):
    """cerate operators, and evaluate graph with single node"""
    def test_constant(self):
        five = Constant(5)
        self.assertEqual( evaluate(five), 5 )

    def test_variable(self):
        x = Variable(1)
        self.assertEqual(evaluate(x), 1)
        x.value = 2
        self.assertEqual(evaluate(x), 2)

    def test_custom_operator_class(self):
        add = Add(Constant(1), Constant(2))
        self.assertEqual(evaluate(add), 3)

    def test_operator_from_function(self):
        def f(a, b):
            return a+b

        Add = operator(f)
        three = Add(Constant(1), Constant(2))
        self.assertEqual(f(1,2), evaluate(three))


class ReconnectInputs(unittest.TestCase):
    def test_setting_inputs(self):
        add = Add()
        add.setInput(0, Constant(1))
        add.setInput(1, Constant(2))

        self.assertEqual(evaluate(add), 3)
        add.setInput(1, Constant(3))
        self.assertEqual(evaluate(add), 4)
        self.setInput("A", Constant(5))
        self.assertEqual(evaluate(add), 8)


class CacheOperator(unittest.TestCase):
    def test_request(self):
        import requests
        
        # create the graph
        url = "https://github.com/zalavariandris/nodeflow"
        Request = operator(lambda url: requests.get(url).text)
        request = Request(Constant(url))

        # evaluate the graph
        result = evaluate(request)

        # test against raw requests lib
        self.assertTrue(requests.get(url).text, result)
        self.assertTrue(result.strip().startswith("<!DOCTYPE html>"))


# class TestCache(unittest.TestCase):
#     def test_cache(self):
#         text = Constant("Hello World")
#         cached = Cache(text)
#         evaluate(cached)


if __name__ == '__main__':
    unittest.main(verbosity=2)