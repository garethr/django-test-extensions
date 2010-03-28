"""
Test runner that doesn't use the database. Contributed by
Bradley Wright <intranation.com>
"""

import os
import unittest
from glob import glob

from django.test.utils import setup_test_environment, teardown_test_environment
from django.conf import settings
from django.test.simple import *

import coverage

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.

    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.

    Returns the number of tests that failed.
    """
    setup_test_environment()

    settings.DEBUG = False
    suite = unittest.TestSuite()

    modules_to_cover = []

    # if passed a list of tests...
    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    # ...otherwise use all installed
    else:
        for app in get_apps():
            # skip apps named "Django" because they use a database
            if not app.__name__.startswith('django'):
                # get the actual app name
                app_name = app.__name__.replace('.models', '')
                # get a list of the files inside that module
                files = glob('%s/*.py' % app_name)
                # remove models because we don't use them, stupid
                new_files = [i for i in files if not i.endswith('models.py')]
                modules_to_cover.extend(new_files)
                # actually test the file
                suite.addTest(build_suite(app))

    for test in extra_tests:
        suite.addTest(test)

    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)

    teardown_test_environment()

    return len(result.failures) + len(result.errors)

def run_tests_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[], xml_out=False):
    """
    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.

    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.

    Returns the number of tests that failed.
    """
    setup_test_environment()

    settings.DEBUG = False
    suite = unittest.TestSuite()

    modules_to_cover = []

    # start doing some coverage action
    cov = coverage.coverage()
    cov.erase()
    cov.start()

    # if passed a list of tests...
    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    # ...otherwise use all installed
    else:
        for app in get_apps():
            # skip apps named "Django" because they use a database
            if not app.__name__.startswith('django'):
                # get the actual app name
                app_name = app.__name__.replace('.models', '')
                # get a list of the files inside that module
                files = glob('%s/*.py' % app_name)
                # remove models because we don't use them, stupid
                new_files = [i for i in files if not i.endswith('models.py')]
                modules_to_cover.extend(new_files)
                # actually test the file
                suite.addTest(build_suite(app))

    for test in extra_tests:
        suite.addTest(test)

    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)

    teardown_test_environment()

    # stop coverage
    cov.stop()

    # output results
    print ''
    print '--------------------------'
    print 'Unit test coverage results'
    print '--------------------------'
    print ''
    if xml_out:
        # using the same output directory as the --xml function uses for testing
        if not os.path.isdir(os.path.join("temp", "xml")):
            os.makedirs(os.path.join("temp", "xml"))
        output_filename = 'temp/xml/coverage_output.xml'
        cov.xml_report(morfs=coverage_modules, outfile=output_filename)
    cov.report(modules_to_cover, show_missing=1)

    return len(result.failures) + len(result.errors)

def run_tests_with_xmlcoverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
   return run_tests_with_coverage(test_labels, verbosity, interactive, extra_tests, xml_out=True) 

