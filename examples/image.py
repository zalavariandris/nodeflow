from nodeflow import Operator

class Read(Operator):
	def __init__(self):
		self._filename = None

	@property
	def filename(self):
		return self._filename

	@filename.setter
	def filename(self, value):
		self._filename = value
	

	def evaluate(self):
		pass

if __name__ == "__main__":
	read = Read()

	read.filename = "hello"


