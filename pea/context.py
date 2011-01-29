__all__ = [
	'step',
	'steps',
	'world',
	'TestCase',
	'Given',
	'When',
	'Then',
	'And',
	]

from formatter import PeaFormatter
import unittest
class StepCollection(object):
	def __setattr__(self, attr, val):
		if hasattr(self, attr):
			raise RuntimeError("step %s is already declared!" % (attr,))
		return super(StepCollection, self).__setattr__(attr, val)

class Object(object): pass
class World(unittest.TestCase):
	def __init__(self):
		self._reset()

	def __getattr__(self, a):
		return getattr(self._current, a)

	def _reset(self):
		self._current = Object()

steps = StepCollection()
world = World()

class StepCollectionWrapper(object):
	def __init__(self, prefix):
		self._prefix = prefix

	def __getattr__(self, a):
		attr = getattr(steps, a)
		return attr(self._prefix)

Given = StepCollectionWrapper('Given')
When = StepCollectionWrapper('When')
Then = StepCollectionWrapper('Then')
And = StepCollectionWrapper('And')

class TestCase(unittest.TestCase):
	def setUp(self):
		global world
		world._reset()

def step(func):
	#print "adding func: %s" % (func.__name__)
	setattr(steps, func.__name__, lambda prefix: PeaFormatter.with_formatting(prefix, func))
	return func

