import coverage
import os
from inspect import getmembers, ismodule

from django.conf import settings
from django.test.simple import run_tests as django_test_runner
from django.db.models import get_app, get_apps
from django.utils.functional import curry

from nodatabase import run_tests as nodatabase_run_tests

def is_wanted_module(mod):
    included = getattr(settings, "COVERAGE_INCLUDE_MODULES", [])
    excluded = getattr(settings, "COVERAGE_EXCLUDE_MODULES", [])
    
    marked_to_include = None 

    for exclude in excluded:
        if exclude.endswith("*"):
            if mod.__name__.startswith(exclude[:-1]):
                marked_to_include = False
        elif mod.__name__ == exclude:
            marked_to_include = False
    
    for include in included:
        if include.endswith("*"):
            if mod.__name__.startswith(include[:-1]):
                marked_to_include = True
        elif mod.__name__ == include:
            marked_to_include = True
    
    # marked_to_include=None handles not user-defined states
    if marked_to_include is None:
        if included and excluded:
            # User defined exactly what they want, so exclude other
            marked_to_include = False
        elif excluded:
            # User could define what the want not, so include other.
            marked_to_include = True
        elif included:
            # User enforced what they want, so exclude other
            marked_to_include = False
        else:
            # Usar said nothing, so include anything
            marked_to_include = True

    return marked_to_include

def get_coverage_modules(app_module):
    """
    Returns a list of modules to report coverage info for, given an
    application module.
    """
    app_path = app_module.__name__.split('.')[:-1]
    coverage_module = __import__('.'.join(app_path), {}, {}, app_path[-1])

    return [coverage_module] + [attr for name, attr in
        getmembers(coverage_module) if ismodule(attr) and name != 'tests']

def get_all_coverage_modules(app_module):
    """
    Returns all possible modules to report coverage on, even if they
    aren't loaded.
    """
    # We start off with the imported models.py, so we need to import
    # the parent app package to find the path.
    app_path = app_module.__name__.split('.')[:-1]
    app_package = __import__('.'.join(app_path), {}, {}, app_path[-1])
    app_dirpath = app_package.__path__[-1]

    mod_list = []
    for root, dirs, files in os.walk(app_dirpath):
        root_path = app_path + root[len(app_dirpath):].split(os.path.sep)[1:]
        excludes = getattr(settings, 'EXCLUDE_FROM_COVERAGE', [])
        if app_path[0] not in excludes:
            for file in files:
                if file.lower().endswith('.py'):
                    mod_name = file[:-3].lower()
                    try:
                        mod = __import__('.'.join(root_path + [mod_name]),
                            {}, {}, mod_name)
                    except ImportError:
                        pass
                    else:
                        mod_list.append(mod)

    return mod_list

def run_tests(test_labels, verbosity=1, interactive=True,
        extra_tests=[], nodatabase=False):
    """
    Test runner which displays a code coverage report at the end of the
    run.
    """
    test_labels = test_labels or getattr(settings, "TEST_APPS", None)
    cover_branch = getattr(settings, "COVERAGE_BRANCH_COVERAGE", False)
    cov = coverage.coverage(branch=cover_branch, cover_pylib=False)
    cov.use_cache(0)
    cov.start()
    if nodatabase:
        results = nodatabase_run_tests(test_labels, verbosity, interactive,
            extra_tests)
    else:
        from django.db import connection
        connection.creation.destroy_test_db = lambda *a, **k: None
        results = django_test_runner(test_labels, verbosity, interactive,
            extra_tests)
    cov.stop()

    coverage_modules = []
    if test_labels:
        for label in test_labels:
            # Don't report coverage if you're only running a single
            # test case.
            if '.' not in label:
                app = get_app(label)
                coverage_modules.extend(get_all_coverage_modules(app))
    else:
        for app in get_apps():
            coverage_modules.extend(get_all_coverage_modules(app))

    morfs = filter(is_wanted_module, coverage_modules)

    report_methd = cov.report
    if getattr(settings, "COVERAGE_HTML_REPORT", False) or \
            os.environ.get("COVERAGE_HTML_REPORT"):
        output_dir = getattr(settings, "COVERAGE_HTML_DIRECTORY", "covhtml")
        report_method = curry(cov.html_report, directory=output_dir)
        print >>sys.stdout
        print >>sys.stdout, "Coverage HTML reports were output to '%s'" %output_dir
    else:
        report_method = cov.report

    morfs and report_method(morfs=morfs)

    return results
