from test_extensions.common import Common

class Examples(Common):
    """
    This class contains a number of example tests using the common custom assertions.
    Note that these tests won't run as they refer to code that does not exist. Note also
    that all tests begin with test_. This ensures the test runner picks them up.
    """
        
    def test_always_pass(self):
        "Demonstration of how to pass a test based on logic"
        self.assertTrue(True)
    
    def test_always_fail(self):
        "Demonstration of how to fail a test based on logic"
        self.assertFalse(False, "Something went wrong")
    
    def test_presense_of_management_command(self):
        "Check to see whether a given management commands is available"
        try:
            call_command('management_command_name')
        except Exception:
            self.assert_("management_command_name management command missing")    

    def test_object_type(self):
        "Simple test to check a given object type"
        example = Object()
        self.assert_is_instance(Object,example)        

    def test_assert_raises(self):
        "Test whether a given function raises a given exception"
        path = os.path.join('/example_directory', 'invalid_file_name')
        self.assert_raises(ExampleException, example_function, path)

    def test_assert_attrs(self):
        "Demonstration of assert_attrs, checks that a given object has a given set of attributes"
        event = Event(title="Title",description="Description")
        self.assert_attrs(event,
          title = 'Title',
          description = 'Description'
        )

    def test_assert_counts(self):
        "Demonstration of assert_counts using a set of fictional objects"
        self.assert_counts([1, 1, 1, 1], [Object1, Object2, Object3, Object4])
  
    def test_assert_code(self):
        "Use the HTTP client to make a request and then check the HTTP status code in the response"
        response = self.client.get('/')
        self.assert_code(response, 200)
        
    def test_creation_of_objects_in_admin(self):
        "Demonstration of an admin test to check successful object creation"
        form = {
            'title':       'title',
            'description': 'description',
        }
        self.login_as_admin()
        self.assert_counts([0], [Object])
        response = self.client.post('/admin/objects/object/add/', form)
        self.assert_code(response, 302)
        self.assert_counts([1], [Object])
            
    def test_you_can_delete_objects_you_created(self):
        "Test object deletion via the admin"
        self.login_as_admin()
        form = {
            'title':       'title',
            'description': 'description',
        }
        self.assert_counts([0], [Object])
        self.client.post('/admin/objects/object/add/', form)
        self.assert_counts([1], [Object])
        response = self.client.post('/admin/objects/object/%d/delete/' % Object.objects.get().id, {'post':'yes'})
        self.assert_counts([0], [Object])
                
    def test_assert_renders(self):
        "Example template tag test to check correct rendering"
        expected = 'output of template tag'
        self.assert_renders('{% load templatetag %}{% templatetag %}', expected)
        
    def test_assert_render_matches(self):
        "Example of testing template tags using regex match"
        self.assert_render_matches(
            r'^/assets/a/common/blah.js\?cachebust=[\d\.]+$',
            '{% load static %}{% static "a/common/blah.js" %}',
        )
        
    def test_simple_addition(self):
        "Pattern for testing input/output of a function"
        for (augend, addend, result, msg) in [
              (1,  2,  3, "1+2=3"),
              (1,  3,  4, "1+3=4"),
            ]:
            self.assert_equal(result,augend.plus(addend))

    def test_response_contains(self):
        "Example of a test for content on a given view"
        response = self.client.get('/example/')
        self.assert_response_contains('<h1>', response)
        self.assert_response_doesnt_contain("Not on page", response)

    def test_using_beautiful_soup(self):
        "Example test for content on a given view, this time using the BeautifulSoup parser"
        response = self.client.get('/example/')
        soup = BeautifulSoup(response.content)
        self.assert_equal("Page Title", soup.find("title").string.strip())
        
    def test_get_tables_that_should_exist(self):
        "Useful pattern for checking for the existence of all required tables"
        tables_that_exist = [row[0] for row in _execute("SHOW TABLES").fetchall()]
        self.assert_equal(True, 'objects_object' in tables_that_exist)