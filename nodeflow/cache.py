from core import Operator, Constant, evaluate
from typing import Callable

import requests


class Request(Operator):
	def __init__(self, url: Constant):
		self.url = url

	def __call__(self, url):
		response = requests.get(url) 
		return response.text


class Cache(Operator):
	def __init__(self, source:Operator, key:Callable=None):
		if key is None:
			key = lambda s: hash(s)

		self.source = source
		self.key = key

	def dependencies(self):
		key = self.key(self.source)
		if key not in cache:
			return [self.source]
		else:
			return []

	def __call__(self, value=None):
		if key not in cache:
			cache[key] = value
		return cache[key]


class Placeholder:
	"""attribute"""
	def __init__(self, value=None):
		self.value = value

	def __call__(self):
		return self.value


class MyGraph(Operator):
	def __init__(self, placeholders):
		self.url = Constant("https://444.hu/")
		self.output = Request(self.url)

	def dependencies(self):
		return []

	def __call__(self)
:		url = self.url()
		text = self.request(url)
		return self.text


if __name__ == "__main__":
	mygraph = MyGraph()
	result = mygraph({url: "https://444.hu/"})
	print(result)
	
		