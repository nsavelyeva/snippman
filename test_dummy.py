import nose
from nose.tools import with_setup

# Can also be setup, setup_module, setUp or setUpModule
def setUpModule(module):
    print ("")
    print ("%s" % (setUpModule.__name__,))

# Can also be teardown, teardown_module, or tearDownModule
def tearDownModule(module):
    print ("%s" % (tearDownModule.__name__,))

def setup_func():
    print ("%s" % (setup_func.__name__,))

def teardown_func():
    print ("%s" % (teardown_func.__name__,))

@with_setup(setup_func, teardown_func)
def test_case_1():
    print ("%s" % (test_case_1.__name__,))

class test_class_1:

    def setup(self):
        print ("%s called before each test method" % (test_class_1.setup.__name__,))

    def teardown(self):
        print ("%s called after each test method" % (test_class_1.teardown.__name__,))

    @classmethod
    def setup_class(cls):
        print ("%s called before any method in this class is executed" % (test_class_1.setup_class.__name__,))

    @classmethod
    def teardown_class(cls):
        print ("%s called after methods in this class is executed" % (test_class_1.teardown_class.__name__,))

    def test_case_2(self):
        print ("%s" % (test_class_1.test_case_2.__name__,))
