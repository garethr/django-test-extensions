import os

# Test classes inherit from the Django TestCase
from django.test import TestCase

# If you're wanting to do direct database queries you'll need this
from django.db import connection

# The BeautifulSoup HTML parser is useful for testing markup fragments
from BeautifulSoup import BeautifulSoup as Soup

# needed to login to the admin
from django.contrib.auth.models import User

class Common(TestCase):
    """
    This class contains a number of custom assertions which
    extend the default Django assertions. Use this as the super 
    class for you tests rather than django.test.TestCase
    """
    
    # a list of fixtures for loading data before each test
    fixtures = []
        
    def setUp(self):
        """
        setUp is run before each test in the class. Use it for
        initilisation and creating mock objects to test
        """        
        pass

    def tearDown(self):
        """
        tearDown is run after each test in the class. Use it for
        cleaning up data created during each test
        """
        pass 

    # A few useful helpers methods
    
    def execute_sql(*sql):
        "execute a SQL query and return the cursor"
        cursor = connection.cursor()
        cursor.execute(*sql)
        return cursor
          
    # Custom assertions
    
    def assert_equal(self, *args, **kwargs):
        "Assert that two values are equal"
        return self.assertEqual(*args, **kwargs)

    def assert_not_equal(self, *args, **kwargs):
        "Assert that two values are not equal"
        return not self.assertNotEqual(*args, **kwargs)
    
    def assert_contains(self, needle, haystack):
        "Assert that one value (the hasystack) contains another value (the needle)"
        return self.assert_(needle in haystack, "Content should contain `%s' but doesn't:\n%s" % (needle, haystack))

    def assert_doesnt_contain(self, needle, haystack):
        "Assert that one value (the hasystack) does not contain another value (the needle)"
        return self.assert_(needle not in haystack, "Content should not contain `%s' but does:\n%s" % (needle, haystack))

    def assert_regex_contains(self, pattern, string, flags=None):
        "Assert that the given regular expression matches the string"
        flags = flags or 0
        self.assertTrue(re.search(pattern, string, flags) != None)
        
    def assert_count(self, expected, model):
        "Assert that their are the expected number of instances of a given model"
        actual = model.objects.count()
        self.assert_equal(expected, actual, "%s should have %d objects, had %d" % (model.__name__, expected, actual))
        
    def assert_counts(self, expected_counts, models):
        "Assert than a list of numbers is equal to the number of instances of a list of models"
        if len(expected_counts) != len(models):
            raise("Number of counts and number of models should be equal")
        actual_counts = [model.objects.count() for model in models]
        self.assert_equal(expected_counts, actual_counts, "%s should have counts %s but had %s" % ([m.__name__ for m in models], expected_counts, actual_counts))

    def assert_is_instance(self, model, obj):
        "Assert than a given object is an instance of a model"
        self.assert_(isinstance(obj, model), "%s should be instance of %s" % (obj, model))
        
    def assert_raises(self, *args, **kwargs):
        "Assert than a given function and arguments raises a given exception"
        return self.assertRaises(*args, **kwargs)

    def assert_attrs(self, obj, **kwargs):
        "Assert a given object has a given set of attribute values"
        for key in sorted(kwargs.keys()):
            expected = kwargs[key]
            actual = getattr(obj, key)
            self.assert_equal(expected, actual, u"Object's %s expected to be `%s', is `%s' instead" % (key, expected, actual))

    def assert_key_exists(self, key, item):
        "Assert than a given key exists in a given item"
        try:
            self.assertTrue(key in item)
        except AssertionError:
            print 'no %s in %s' % (key, item)
            raise AssertionError 

    def assert_file_exists(self, file_path):
        "Assert a given file exists"
        self.assertTrue(os.path.exists(file_path), "%s does not exist!" % file_path)

    def assert_has_attr(self, obj, attr):
        "Assert a given object has a give attribute, without checking the values"
        try:
            getattr(obj, attr)
            assert(True)
        except AttributeError:
            assert(False)
