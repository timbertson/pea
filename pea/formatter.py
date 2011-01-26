import os
import sys
import nose
import functools
import termstyle

failure = 'FAILED'
error = 'ERROR'
success = 'passed'
skip = 'skipped'
line_length = 77

class DevNull(object):
	def write(self, msg): pass
	def writeln(self, msg=''): pass
	def flush(self): pass
	
class PeaFormatter(nose.plugins.Plugin):
	name = 'pea'
	score = 601
	instance = None
	_newtest = False
	
	def __init__(self, *args):
		self.enabled = False
		type(self).instance = self

	def configure(self, options, conf):
		self.enabled = options.verbosity >= 2
		if not self.enabled: return
		color = getattr(options, 'color', True)
		force_color = getattr(options, 'force_color', False)
		if color:
			try:
				(termstyle.enable if force_color else termstyle.auto)()
			except TypeError: # happens when stdout is closed
				pass

	def beforeTest(self, test):
		if self.enabled:
			print >> sys.stderr, ""
		type(self)._newtest = True
	
	@classmethod
	def with_formatting(cls, prefix, func):
		def prn(s):
			if cls.instance and cls.instance.enabled:
				if cls._newtest:
					print >> sys.stderr, ""
					cls._newtest = False
				print >> sys.stderr, s

		@functools.wraps(func)
		def _run(*a, **kw):
			name = func.__name__.replace('_', ' ')
			desc = "\t%s %s" % (prefix, ' '.join([
					name,
					termstyle.bold(' '.join(map(repr,a))),
					' '.join(["%s=%r" % (k, termstyle.bold(v)) for k,v in kw.items()])])
			)
			try:
				ret = func(*a, **kw)
				prn(termstyle.green(desc))
				return ret
			except:
				prn(termstyle.red(desc))
				raise
		return _run

