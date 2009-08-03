# Test classes inherit from the Django TestCase
from common import Common

# needed to login to the admin
from django.contrib.auth.models import User

from django.template import Template, Context

class DjangoCommon(Common):
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
          
    def login_as_admin(self):
        "Create, then login as, an admin user"
        # Only create the user if they don't exist already ;)
        try:
            User.objects.get(username="admin")
        except User.DoesNotExist:
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
        
    def assert_code(self, response, code):
        "Assert that a given response returns a given HTTP status code"
        self.assertEqual(code, response.status_code, "HTTP Response status code %d expected, but got %d" % (code, response.status_code))
            
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