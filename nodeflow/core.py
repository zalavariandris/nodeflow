from typing import Union, List, Dict, Any, Generator, Callable
from collections import OrderedDict
from collections.abc import Hashable
from collections import Counter

class Operator:
    namecounter = Counter()
    def __init__(self, *args, name:str=None, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.name = name
        if self.name is None:
            self.name = f"{self.__class__.__name__}"
        self.namecounter[self.name]+=1
        if self.namecounter[self.name]>0:
            self.name  += "#{:03d}".format(self.namecounter[self.name])

    def dependencies(self)->Generator["Operator", None, None]:
        for dep in self.args:
            yield dep

        for dep in self.kwargs.values():
            yield dep

    def key(self):
        tuple([arg.key() for arg in self.args])
        return (
            self.__class__.__name__, 
            tuple([arg.key() for arg in self.args]),
            tuple([arg.key() for arg in self.kwargs.values()])
        )

    def __hash__(self):
        return id(self)

    def __call__(self)->Any:
        return None

    def __repr__(self)->str:
        return f"'{self.name}'[{self.__class__.__name__}]"

    def __str__(self)->str:
        return self.name if self.name else self.__class__.__name__


class Constant(Operator):
    def __init__(self, value):
        super().__init__()
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
			print("put key in cache", key)
			self.cache[key] = value
		return self.cache[self.source.key()]

	def key(self):
		return self._key()

def operator(f):
    class Op(Operator):
        def __init__(self, *args, **kwargs):
            assert all(isinstance(arg, Operator) for arg in args)
            assert all(isinstance(arg, Operator) for arg in kwargs.values())
            super().__init__(*args, **kwargs)

        def __call__(self, *args, **kwags):
            return f(*args, **kwags)

        def repr(self):
            return f"operator({f.__name__})"

    return Op


def test_dependency_order(ordered_nodes):
    indices = [i for i, node in enumerate(ordered_nodes)]
    for N in ordered_nodes:
        for S in N.dependencies():
            assert ordered_nodes.index(S) < ordered_nodes.index(N)

def graph(root:Operator):
    # Run a depth first search on root node to create the dependency graph
    # order is important when evaluating
    G: Dict[Operator, List[Operator]] = OrderedDict()
    queue = [root]
    while queue:
        N = queue.pop()
        if N not in G:
            G[N] = list()
            for S in N.dependencies():
                queue.append(S)
                G[N].append(S)

    return G


def evaluate(root:Operator, verbose=False):
    """Evaluate Graph"""
    if verbose: print("==EVALUATE GRAPH==\n==================\n")

    #if verbose: print("Create Graph (dependency)\n------------")

    # Run a depth first search on root node to create the dependency graph
    # order is important when evaluating
    G: Dict[Operator, List[Operator]] = OrderedDict()
    queue = [root]
    while queue:
        N = queue.pop()
        if N not in G:
            G[N] = list()
            for S in N.dependencies():
                queue.append(S)
                G[N].append(S)

    # Show dependency graph
    #if verbose: 
    #    for N, deps in G.items():
    #        print(f"  {N}: {deps}")
    #    print()

    if verbose: print("Reverse Graph (dependants)\n-------------")
    # Reverse G to create dependants graph
    # since the nodes order is based on DFS revert edges will result in reversed TopologicalSort: 
    # Dependant Nodes will come after dependency Nodes
    G1: OrderedDict[Operator, List[Operator]] = OrderedDict({root: []})   
    for N, deps in G.items():
        for S in deps:
            if S not in G1:
                G1[S] = list()
            G1[S].append(N)

    # show dependant graph
    if verbose:
        for N, deps in G1.items():
            print(f"  {N}: {deps}")
        print()

    # Evaluate nodes in topological order
    if verbose: print("Evaluate Nodes\n--------------")
    topological_order = list(reversed(G1.keys()))

    # push results to arguments dictionary to keep results
    arguments = {N: list() for N in G.keys()}
    for N in topological_order:
        args = list( reversed(arguments[N]) )
        value = N(*args) # evaluate node with arguments
        if verbose:
            print(f"  {N}({', '.join(repr(arg)[:10] for arg in args)}) => {repr(value)[:10]}")
        del arguments[N] # delete results used for evaluation

        # push results forward
        for T in G1[N]:
            arguments[T].append(value)
    if verbose: print()

    # arguments shoud be empty now
    assert(len(arguments)==0)

    # return the last evaluated value
    return value


if __name__ == "__main__":
    import numpy as np
    op = Constant("hello")
    result = evaluate(op)
    print(result)




