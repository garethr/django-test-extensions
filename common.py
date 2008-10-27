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
      
    def login_as_admin(self):
        "Create, then login as, an admin user"
        user = User.objects.create_user('admin', 'admin@example.com', 'password')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        if not self.client.login(username='admin', password='password'):
            raise Exception("Login failed")
  
    # Some assertions need to know which template tag libraries to load
    # so we provide a list of templatetag libraries        
    template_tag_libraries = []

    def render(self, template, **kwargs):
        "Return the rendering of a given template including loading of template tags"        
        template = "".join(["{%% load %s %%}" % lib for lib in self.template_tag_libraries]) + template
        return Template(template).render(Context(kwargs)).strip()
  
    # Custom assertions
    
    def assert_equal(self, *args, **kwargs):
        "Assert that two values are equal"
        return self.assertEqual(*args, **kwargs)

    def assert_not_equal(self, *args, **kwargs):
        "Assert that two values are not equal"
        return not self.assertEqual(*args, **kwargs)
    
    def assert_contains(self, needle, haystack):
        "Assert that one value (the hasystack) contains another value (the needle)"
        return self.assert_(needle in haystack, "Content should contain `%s' but doesn't:\n%s" % (needle, haystack))

    def assert_doesnt_contain(self, needle, haystack):
        "Assert that one value (the hasystack) does not contain another value (the needle)"
        return self.assert_(needle not in haystack, "Content should not contain `%s' but does:\n%s" % (needle, haystack))

    def assert_response_contains(self, fragment, response):
        "Assert that a response object contains a given string"
        self.assert_(fragment in response.content, "Response should contain `%s' but doesn't:\n%s" % (fragment, response.content))

    def assert_response_doesnt_contain(self, fragment, response):
        "Assert that a response object does not contain a given string"
        self.assert_(fragment not in response.content, "Response should not contain `%s' but does:\n%s" % (fragment, response.content))

    def assert_regex_contains(self, pattern, string, flags=None):
        "Assert that the given regular expression matches the string"
        flags = flags or 0
        self.assertTrue(re.search(pattern, string, flags) != None)

    def assert_render_matches(self, template, match_regexp, vars={}):
        "Assert than the output from rendering a given template with a given context matches a given regex"
        r = re.compile(match_regexp)
        actual = Template(template).render(Context(vars))
        self.assert_(r.match(actual), "Expected: %s\nGot: %s" % (
            match_regexp, actual
        ))
        
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

    def assert_code(self, response, code):
        "Assert that a given response returns a given HTTP status code"
        self.assertEqual(code, response.status_code, "HTTP Response status code %d expected, but got %d" % (code, response.status_code))
        
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
    
    def assert_render(self, expected, template, **kwargs):
        "Asserts than a given template and context render a given fragment"
        self.assert_equal(expected, self.render(template, **kwargs))

    def assert_render_matches(self, match_regexp, template, vars={}):
        r = re.compile(match_regexp)
        actual = Template(template).render(Context(vars))
        self.assert_(r.match(actual), "Expected: %s\nGot: %s" % (
            match_regexp, actual
        ))

    def assert_doesnt_render(self, expected, template, **kwargs):
        "Asserts than a given template and context don't render a given fragment"
        self.assert_not_equal(expected, self.render(template, **kwargs))

    def assert_render_contains(self, expected, template, **kwargs):
        "Asserts than a given template and context rendering contains a given fragment"
        self.assert_contains(expected, self.render(template, **kwargs))

    def assert_render_doesnt_contain(self, expected, template, **kwargs):
        "Asserts than a given template and context rendering does not contain a given fragment"
        self.assert_doesnt_contain(expected, self.render(template, **kwargs))