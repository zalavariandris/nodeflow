import nodeflow as nf
import unittest

class MathOperations(unittest.TestCase):
    """crate operators, and evaluate graph with single node"""
    def test_math(self):
        one = nf.Constant(1)
        five = nf.Constant(5)
        plus = nf.Plus(one, five)
        minus = nf.Minus(five, one)
        divide = nf.Divide(plus, minus)
        mult = nf.Multiply(divide, five)
        output = mult

        # evaluate
        result = output.evaluate(verbose=True)
        expected = (1+5) / (5-1) * 5
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)