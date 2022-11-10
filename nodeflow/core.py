from typing import Union, List, Dict, Any, Generator, Callable
from collections import OrderedDict
from collections.abc import Hashable
from collections import Counter
import inspect
import networkx as nx


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Operator:
    namecounter = Counter()
    def __init__(self, *args, name:str=None, **kwargs):
        self.args = list(args)
        self.kwargs = kwargs
        self._name = self.make_unique_name(name or self.__class__.__name__)

    @classmethod
    def copy(cls, op):
        pass

    @classmethod
    def make_unique_name(cls, name:str):
        cls.namecounter[name]+=1
        if cls.namecounter[name]>0:
            name  += "#{:03d}".format(cls.namecounter[name])
        return name
        self.signature = inspect.signature(self.__call__)

    def set_inputs(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def dependencies(self)->Generator["Operator", None, None]:
        for dep in self.args:
            yield dep

        for dep in self.kwargs.values():
            yield dep

    def key(self):
        tuple(arg.key() for arg in self.args)
        return (
            self.__class__.__name__, 
            tuple(arg.key() for arg in self.args),
            tuple(arg.key() for arg in self.kwargs.values())
        )

    def __hash__(self):
        return id(self)

    def __call__(self)->Any:
        return None

    def __repr__(self)->str:
        return self._name

    def graph(self, verbose=False):
        """
        Dependancy graph:
          Run a depth first search on root node to create the dependency graph
          order is important when evaluating
        """
        G: Dict[Operator, List[Operator]] = OrderedDict()
        queue = [self]
        while queue:
            N = queue.pop()
            if N not in G:
                G[N] = list()
                for S in N.dependencies():
                    queue.append(S)
                    G[N].append(S)

        
        if verbose:
            print("\nGraph:")
            for op, args in G.items():
                print(f"  {op} {args}")

        return G

    def evaluate(self, verbose=False):
        """Evaluate Graph"""
        # if verbose: print("==EVALUATE GRAPH==\n==================\n")

        #if verbose: print("Create Graph (dependency)\n------------")
        G = self.graph(verbose=verbose)
        G1 = nx.to_dict_of_lists(nx.DiGraph(G).reverse())

        # Evaluate nodes in order
        # if verbose: print("Evaluate Nodes\n--------------")
        evaluation_order = list(reversed(list(nx.topological_sort(nx.DiGraph(G)))))
        # if verbose: print("  in order:", evaluation_order)


        # keep results as arguments
        if verbose: print("\nEvaluate graph (in order:", evaluation_order, ")")
        arguments = {N: list() for N in G.keys()}
        for N in evaluation_order:
            args = [n for n in reversed(arguments[N])]
            if verbose: print(f"  evaluate: {N} with arguments: {args}")
            value = N(*args) # evaluate node with arguments
            if verbose:
                print(f"    {N}({', '.join(repr(arg)[:10] for arg in args)}) => {repr(value)[:10]}")
            del arguments[N] # delete results used for evaluation

            # push results forward
            for T in G1[N]:
                arguments[T].append(value)
        if verbose: print()

        # arguments shoud be empty now
        assert(len(arguments)==0)

        # return the last evaluated value
        return value


def operator(f, name=None):
    # print("make operator from function", f.__name__)
    class Op(Operator):
        def __init__(self, *args, **kwargs):
            assert all(isinstance(arg, Operator) for arg in args)
            assert all(isinstance(arg, Operator) for arg in kwargs.values())
            super().__init__(*args, name=name or f.__name__, **kwargs)
            # self._f = f
            # print("SET operator name to:", self._name)

        def __call__(self, *args, **kwags):
            return f(*args, **kwags)

    return Op


class Constant(Operator):
    def __init__(self, value, name=None):
        super().__init__(name=name)
        self.value = value

    def __call__(self):
        return self.value

    def key(self):
        return id(self.value)


class Variable(Operator):
    def __init__(self, value):
        super().__init__()
        assert isinstance(value, Hashable)
        self.value = value

    def __call__(self):
        return self.value

    def key(self):
        return ("var", self.value)

    def __str__(self):
        return str(self.value)


class Cache(Operator):
	def __init__(self, source:Operator, key:Callable=None):
		super().__init__()
		if key is None:
			key = lambda s: hash(s)

		self.source = source
		self._key = key
		if not self._key is None:
			self._key = lambda: source.key()


		self.cache = dict()

	def __hash__(self):
		return hash( ("Cache", self.source) )

	def dependencies(self):
		if self.source.key() not in self.cache:
			return [self.source]
		else:
			return []

	def __call__(self, value=None):
		if value is not None:
			key = self.source.key()
			self.cache[key] = value
		return self.cache[self.source.key()]

	def key(self):
		return self._key()

import datetime
class Log(Operator):
    def __init__(self, value:Operator, fmt:str="{timestamp} {value}", name=None):
        super().__init__(value, name=name)
        self.fmt = fmt

    def __call__(self, value):
        print(self.fmt.format(timestamp=str(datetime.datetime.now()), value=value))
        return value
        

def test_dependency_order(ordered_nodes):
    indices = [i for i, node in enumerate(ordered_nodes)]
    for N in ordered_nodes:
        for S in N.dependencies():
            assert ordered_nodes.index(S) < ordered_nodes.index(N)

# def graph(root:Operator):
#     # Run a depth first search on root node to create the dependency graph
#     # order is important when evaluating
#     G: Dict[Operator, List[Operator]] = OrderedDict()
#     queue = [root]
#     while queue:
#         N = queue.pop()
#         if N not in G:
#             G[N] = list()
#             for S in N.dependencies():
#                 queue.append(S)
#                 G[N].append(S)

#     return G



if __name__ == "__main__":
    import numpy as np
    op = Constant("hello")
    result = op.evaluate()
    print(result)




