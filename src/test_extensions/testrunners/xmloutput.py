import time, traceback, string
from unittest import TestResult

from xmlunit.unittest import _WritelnDecorator, XmlTextTestRunner as his_XmlTextTestRunner

from django.test.simple import *
from django.utils.html import escape

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    setup_test_environment()

    settings.DEBUG = False
    suite = unittest.TestSuite()

    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    else:
        for app in get_apps():
            suite.addTest(build_suite(app))

    for test in extra_tests:
        suite.addTest(test)

    old_name = settings.DATABASE_NAME
    from django.db import connection
    connection.creation.create_test_db(verbosity, autoclobber=not interactive)
    result = XMLTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, verbosity)

    teardown_test_environment()

    return len(result.failures) + len(result.errors)


class XMLTestRunner(his_XmlTextTestRunner):
    def _makeResult(self):
        return _XmlTextTestResult(self.testResults, self.descriptions, self.verbosity)

class _XmlTextTestResult(unittest.TestResult):
    """A test result class that can print xml formatted text results to a stream.

    Used by XmlTextTestRunner.
    """
    #separator1 = '=' * 70
    #separator2 = '-' * 70
    def __init__(self, stream, descriptions, verbosity):
        TestResult.__init__(self)
        self.stream = _WritelnDecorator(stream)
        self.showAll = verbosity > 1
        self.descriptions = descriptions
        self._lastWas = 'success'
        self._errorsAndFailures = ""
        self._startTime = 0.0
        self.params=""

    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def startTest(self, test):  #  CONSIDER  why are there 2 startTests in here?
        self._startTime = time.time()
        test._extraXML = ''
        test._extraAssertions = []
        TestResult.startTest(self, test)
        self.stream.write('<testcase classname="%s' % test.__class__.__name__ + '" name="%s' % test.id().split('.')[-1] + '"')
        desc = test.shortDescription()

        if desc:
            desc = _cleanHTML(desc)
            self.stream.write(' desc="%s"' % desc)

    def stopTest(self, test):
        stopTime = time.time()
        deltaTime = stopTime - self._startTime
        TestResult.stopTest(self, test)
        self.stream.write(' time="%.3f"' % deltaTime)
        self.stream.write('>')
        if self._lastWas != 'success':
            if self._lastWas == 'error':
                self.stream.write(self._errorsAndFailures)
            elif self._lastWas == 'failure':
                self.stream.write(self._errorsAndFailures)
            else:
                assert(False)

        seen = {}

        for assertion in test._extraAssertions:
            if not seen.has_key(assertion):
                self._addAssertion(assertion[:110]) # :110 avoids tl;dr TODO use a lexical truncator
                seen[assertion] = True

        self.stream.write('</testcase>')
        self._errorsAndFailures = ""

        if test._extraXML != '':
            self.stream.write(test._extraXML)

    def _addAssertion(self, diagnostic):
        diagnostic = _cleanHTML(diagnostic)
        self.stream.write('<assert>' + diagnostic + '</assert>')

    def addSuccess(self, test):
        TestResult.addSuccess(self, test)
        self._lastWas = 'success'

    def addError(self, test, err):
        TestResult.addError(self, test, err)
        if err[0] is KeyboardInterrupt:
            self.shouldStop = 1
        self._lastWas = 'error'
        self._errorsAndFailures += '<error type="%s">' % err[0].__name__
        for line in apply(traceback.format_exception, err):
           for l in string.split(line,"\n")[:-1]:
              self._errorsAndFailures += "%s" % l
        self._errorsAndFailures += "</error>"

    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        if err[0] is KeyboardInterrupt:
            self.shouldStop = 1
        self._lastWas = 'failure'
        self._errorsAndFailures += '<failure type="%s">' % err[0].__name__
        for line in apply(traceback.format_exception, err):
           for l in string.split(line,"\n")[:-1]:
              self._errorsAndFailures += "%s" % l
        self._errorsAndFailures += "</failure>"

    def printErrors(self):
        pass #assert False

    def printErrorList(self, flavour, errors):
        assert False

def _cleanHTML(whut):
    return whut.replace('"', '&quot;'). \
                replace('<', '&lt;').  \
                replace('>', '&gt;')
