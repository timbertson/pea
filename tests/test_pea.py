from __future__ import print_function
from pea import *

FEATURE_FILE="""
from pea import *
import steps
class TestFoo(TestCase):
	def test_output(self):
		Given.my_setup("argument")
		When.I_do_foo(keyword_arg=123, second_arg=456)
		And.I_do_bar()
		Then.foo_and_bar_happen()
"""

PASSING_STEPS = """
from pea import *
@step
def my_setup(a): pass

@step
def I_do_foo(**k): pass

@step
def I_do_bar(): pass

@step
def foo_and_bar_happen(): pass
"""

import tempfile
import shutil
from os.path import join
import os
import subprocess
import itertools
import re

@step
def I_have_a_feature_file_with(contents):
	with open(join(world.dir, 'test_feature.py'), 'w') as f:
		f.write(contents)

@step
def I_have_defined_steps(contents):
	with open(join(world.dir, 'steps.py'), 'w') as f:
		f.write(contents)

@step
def I_run_nosetests(*args):
	p = subprocess.Popen(['nosetests'] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdout, _ = p.communicate()
	world.nose_output = stdout.decode('utf-8')
	world.nose_success = p.returncode == 0

@step
def the_output_should_be(expected, ignoring_summary=True):
	actual = world.nose_output
	if ignoring_summary:
		actual = '\n'.join(itertools.takewhile(lambda line: '--------' not in line, actual.splitlines()))
	actual = actual.replace(str(termstyle.green), '{green}')
	actual = actual.replace(str(termstyle.reset), '{reset}')
	actual = actual.replace(str(termstyle.bold), '{bold}')
	actual = re.sub(r'(tests? run in )[^ ]+( seconds)', r'\1{time}\2', actual)
	try:
		world.assertEquals(actual, expected)
	except AssertionError:
		print(actual)
		raise

@step
def the_output_should_contain(expected):
	assert expected in world.nose_output


import termstyle
class TestPea(TestCase):
	def setUp(self):
		super(TestPea, self).setUp()
		world.dir = tempfile.mkdtemp()
		os.chdir(world.dir)
	
	def tearDown(self):
		shutil.rmtree(world.dir)
		super(TestPea, self).tearDown()

	def test_basic_output(self):
		Given.I_have_a_feature_file_with(FEATURE_FILE)
		And.I_have_defined_steps(PASSING_STEPS)
		When.I_run_nosetests('-v', '--force-color')
		Then.the_output_should_be("""test_output (test_feature.TestFoo) ... 
{green}    Given my setup{reset} {green}{bold}argument{reset}{reset}
{green}    When I do foo{reset} {green}keyword_arg={bold}123{reset}{reset} {green}second_arg={bold}456{reset}{reset}
{green}    And I do bar{reset}
{green}    Then foo and bar happen{reset}
{green}passed{reset}

""")
	
	def test_non_coloured_output(self):
		Given.I_have_a_feature_file_with(FEATURE_FILE)
		And.I_have_defined_steps(PASSING_STEPS)
		When.I_run_nosetests('-v', '--no-color')
		Then.the_output_should_be("""test_output (test_feature.TestFoo) ... 
    Given my setup argument
    When I do foo keyword_arg=123 second_arg=456
    And I do bar
    Then foo and bar happen
ok

""")
	
	def test_non_verbose_output(self):
		Given.I_have_a_feature_file_with(FEATURE_FILE)
		And.I_have_defined_steps(PASSING_STEPS)
		When.I_run_nosetests()
		Then.the_output_should_be('.')
	
	def test_missing_step(self):
		Given.I_have_a_feature_file_with(FEATURE_FILE)
		And.I_have_defined_steps("")
		When.I_run_nosetests('-v')
		Then.the_output_should_contain("AttributeError: 'StepCollection' object has no attribute 'my_setup'")
	
	def test_using_world(self):
		Given.I_have_a_feature_file_with("""
from pea import *
@step
def I_save(val):
	world.val = val

@step
def I_dont_save_anything(): pass

@step
def I_get(val):
	assert world.val == val


class TestFoo(TestCase):
	def test_success(self):
		Given.I_save(1)
		Then.I_get(1)
	def test_failure(self):
		Given.I_dont_save_anything()
		Then.I_get(1)
""")
		When.I_run_nosetests('-v')
		Then.the_output_should_be("""test_failure (test_feature.TestFoo) ... 
    Given I dont save anything
    Then I get 1
ERROR

test_success (test_feature.TestFoo) ... 
    Given I save 1
    Then I get 1
passed

""")


