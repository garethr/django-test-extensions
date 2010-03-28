import os
import re

# Test classes inherit from the Django TestCase
from django.test import TestCase

# If you're wanting to do direct database queries you'll need this
from django.db import connection

# The BeautifulSoup HTML parser is useful for testing markup fragments
from BeautifulSoup import BeautifulSoup as Soup

# needed to login to the admin
from django.contrib.auth.models import User
from django.utils.encoding import smart_str


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
        'Assert that two values are equal'

        return self.assertEqual(*args, **kwargs)

    def assert_not_equal(self, *args, **kwargs):
        "Assert that two values are not equal"
        return not self.assertNotEqual(*args, **kwargs)

    def assert_contains(self, needle, haystack, diagnostic=''):
        'Assert that one value (the hasystack) contains another value (the needle)'
        diagnostic = diagnostic + "\nContent should contain `%s' but doesn't:\n%s" % (needle, haystack)
        diagnostic = diagnostic.strip()
        return self.assert_(needle in haystack, diagnostic)

    def assert_doesnt_contain(self, needle, haystack):  #  CONSIDER  deprecate me for deny_contains
        "Assert that one value (the hasystack) does not contain another value (the needle)"
        return self.assert_(needle not in haystack, "Content should not contain `%s' but does:\n%s" % (needle, haystack))

    def deny_contains(self, needle, haystack):
        "Assert that one value (the hasystack) does not contain another value (the needle)"
        return self.assert_(needle not in haystack, "Content should not contain `%s' but does:\n%s" % (needle, haystack))

    def assert_regex_contains(self, pattern, string, flags=None):
        'Assert that the given regular expression matches the string'
        flags = flags or 0
        disposition = re.search(pattern, string, flags)
        self.assertTrue(disposition != None, repr(smart_str(pattern)) + ' should match ' + repr(smart_str(string)))

    def deny_regex_contains(self, pattern, slug):
        'Deny that the given regular expression pattern matches a string'

        r = re.compile(pattern)

        self.assertEqual( None,
                          r.search(smart_str(slug)),
                          pattern + ' should not match ' + smart_str(slug) )

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

    def _xml_to_tree(self, xml, forgiving=False):
        from lxml import etree
        self._xml = xml

        if not isinstance(xml, basestring):
            self._xml = str(xml)  #  TODO  tostring
            return xml

        if '<html' in xml[:200]:
            parser = etree.HTMLParser(recover=forgiving)
            return etree.HTML(str(xml), parser)
        else:
            parser = etree.XMLParser(recover=forgiving)
            return etree.XML(str(xml))

    def assert_xml(self, xml, xpath, **kw):
        'Check that a given extent of XML or HTML contains a given XPath, and return its first node'
        tree = self._xml_to_tree(xml, forgiving=kw.get('forgiving', False))
        nodes = tree.xpath(xpath)
        self.assertTrue(len(nodes) > 0, xpath + ' should match ' + self._xml)
        node = nodes[0]
        if kw.get('verbose', False):
            self.reveal_xml(node)
        return node

    def reveal_xml(self, node):
        'Spews an XML node as source, for diagnosis'
        from lxml import etree
        print etree.tostring(node, pretty_print=True)

    def deny_xml(self, xml, xpath):
        'Check that a given extent of XML or HTML does not contain a given XPath'
        tree = self._xml_to_tree(xml)
        nodes = tree.xpath(xpath)
        self.assertEqual(0, len(nodes), xpath + ' should not appear in ' + self._xml)