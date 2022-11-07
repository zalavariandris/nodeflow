import nodeflow as nf
import unittest


class MyOp(nf.Operator):
    def __init__(self, A=nf.Constant(0), B=nf.Constant(0)):
        super().__init__(A, B)

    def __call__(self, a, b):
        return a+b

@nf.operator
def MyFunction(a=1, b=10):
    print("run my function")

class OperatorNames(unittest.TestCase):
    def test_unique_name(self):
        op = nf.Operator()
        self.assertEqual(f"{op}", "Operator#001")

        add = MyOp()
        self.assertEqual(f"{add}", "MyOp#001")

        myf = MyFunction()
        self.assertEqual(f"{myf}", "MyFunction#001")

if __name__ == '__main__':
    unittest.main(verbosity=2)