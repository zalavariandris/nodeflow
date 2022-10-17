class Node:
	def __init__(self):
		pass

	def inlets(self):
		for key, value in self.__dict__.items():
			if isinstance(value, Inlet):
				yield value

	# receive the evauated arguments
	def evaluate(self):
		print(f"{self.__class__.__name__}=>evaluate")

	def push(self):
		pass

class Inlet:
	def __init__(self, source:Node):
		self.source = source

class Constant(Node):
	def __init__(self, value):
		self.value = value

	def evaluate(self):
		super().evaluate()
		return self.value

class Plus(Node):
	def __init__(self, A:Node, B:Node):
		self.A = Inlet(A)
		self.B = Inlet(B)

	def evaluate(self, a:int, b:int)->int:
		super().evaluate()
		return a+b

def evaluate_graph(root):
	# Breadth first search
	Q = [root]
	visited = []
	while len(Q)>0:
		n = Q.pop()
		for source in [inlet.source for inlet in n.inlets()]:
			if source not in visited:
				Q.append(source)
				visited.append(source)
	
	print("evaluation order: ", list(reversed(visited)))
	values = dict()
	for n in reversed(visited):
		sources = [inlet.source for inlet in n.inlets()]
		args = [values[s] for s in sources]
		values[n] = n.evaluate(*args)

	print(f"values: {values.values()}")


if __name__ == "__main__":
	one = Constant(1)
	two = Constant(2)
	plus = Plus(one, two)
	plus2 = Plus(plus, two)
	
	result = evaluate_graph(plus2)
	print(result) 