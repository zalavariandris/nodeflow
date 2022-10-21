from core import Operator, Constant, evaluate
from typing import Callable

from functools import partial


class Cache(Operator):
	def __init__(self, source:Operator, key:Callable=None):
		super().__init__()
		if key is None:
			key = lambda s: hash(s)

		self.source = source
		self.key = key
		if not key:
			self.key = partial(hash, self.source.args + tuple(self.source.kwargs.values()))


		self.cache = dict()

	def __hash__(self):
		return hash( ("Cache", self.source) )

	def dependencies(self):
		if self.source not in self.cache:
			return [self.source]
		else:
			return []

	def __call__(self, value=None):
		if value is not None:
			self.cache[self.source] = value
		return self.cache[self.source]


if __name__ == "__main__":
	import requests


	class Request(Operator):
		def __init__(self, url: Constant):
			super().__init__()
			self.url = url

		def __call__(self, url):
			print("call", self)
			response = requests.get(url)
			return response.text

	class StripHTML(Operator):
		def __init__(self, html: Operator):
			super().__init__()
			self.html:Operator = html

		def __call__(self, html:str):
			import re
			return re.sub('<[^<]+?>', '', html)


	url = Constant("https://444.hu/2022/10/18/50-meternyi-darab-szakadt-ki-az-eszaki-aramlatbol-a-robbantas-utan")
	request = Request(url)
	cached_request = Cache(request)
	strip = StripHTML(cached_request)
	output = strip

	# cache works if call Request print only once!
	evaluate(strip)
	result = evaluate(strip)
	#print(result)

	
	
	# print("PYTHONFLOW")
	# import pythonflow as pf
	# CACHE = dict()
	# def save(key, obj):
	# 	global CACHE
	# 	CACHE[key] = obj

	# def load(key):
	# 	global CACHE
	# 	return CACHE[key]


	# with pf.Graph() as graph:
	#     seq = pf.constant([1,2,3,4,5])
	#     cached = pf.cache(seq, save, load)
	#     filtered = pf.filter_(lambda i: i<3, cached)

	# result = graph(filtered)
	# print(result)


	
		