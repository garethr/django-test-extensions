import os
import commands

from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.simple import run_tests as django_test_runner

import figleaf
 
def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    setup_test_environment()
    figleaf.start()
    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)
    figleaf.stop()
    if not os.path.isdir(os.path.join("temp", "figleaf")): os.makedirs(os.path.join("temp", "figleaf"))
    file_name = "temp/figleaf/test_output.figleaf"
    figleaf.write_coverage(file_name)
    output = commands.getoutput("figleaf2html " + file_name + " --output-directory=temp/figleaf")
    print output
    return test_results