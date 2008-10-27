# Test classes inherit from the Django TestCase
from django.test import TestCase

# Twill provides a simple DSL for a number of functional tasks
import twill as twill
from twill import commands as tc

class TwillCommon(TestCase):
    """
    A Base class for using with Twill commands. Provides a few helper methods and setup.
    """
    def setUp(self):
        "Run before all tests in this class, sets the output to the console"
        twill.set_output(StringIO())

    def find(self,regex):
        """
        By default Twill commands throw exceptions rather than failures when 
        an assertion fails. Here we wrap the Twill find command and return
        the expected response along with a helpful message.     
        """
        try:
            tc.go(self.url)
            tc.find(regex) 
        except TwillAssertionError:
            self.fail("No match to '%s' on %s" % (regex, self.url))

    def code(self,status):
        """
        By default Twill commands throw exceptions rather than failures when 
        an assertion fails. Here we wrap the Twill code command and return
        the expected response along with a helpful message.     
        """
        try:
            tc.go(self.url)
            tc.code(status)
        except TwillAssertionError:
            self.fail("%s did not return a %s" % (self.url, status))