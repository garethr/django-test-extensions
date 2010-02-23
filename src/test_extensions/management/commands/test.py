import sys
from optparse import make_option

from django.core import management
from django.conf import settings
from django.db.models import get_app, get_apps
from django.core.management.base import BaseCommand

skippers = []

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    if '--verbosity' not in [opt.get_opt_string() for opt in BaseCommand.option_list]:
        option_list += \
            make_option('--verbosity', action='store', dest='verbosity',
                default='0',
                type='choice', choices=['0', '1', '2'],
                help='Verbosity level; 0=minimal, 1=normal, 2=all'),

    option_list += (
        make_option('--noinput', action='store_false', dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--coverage', action='store_true', dest='coverage',
            default=False,
            help='Show coverage details'),
        make_option('--figleaf', action='store_true', dest='figleaf',
            default=False,
            help='Produce figleaf coverage report'),
        make_option('--xml', action='store_true', dest='xml', default=False,
            help='Produce xml output for cruise control'),
        make_option('--nodb', action='store_true', dest='nodb', default=False,
            help='No database required for these tests'),
        #make_option('--skip', action='store', dest='skip', default=False,
        #    help='Omit these applications from testing'),  #  TODO  require args if used
    )
    help = """Custom test command which allows for
        specifying different test runners."""
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)

        # it's quite possible someone, lets say South, might have stolen
        # the syncdb command from django. For testing purposes we should
        # probably put it back. Migrations don't really make sense
        # for tests. Actually the South test runner does this too.
        management.get_commands()
        management._commands['syncdb'] = 'django.core'

        if options.get('nodb'):
            if options.get('coverage'):
                test_runner_name = 'test_extensions.testrunners.nodatabase.run_tests_with_coverage'
            else:
                test_runner_name = 'test_extensions.testrunners.nodatabase.run_tests'
        elif options.get('coverage'):
            test_runner_name = 'test_extensions.testrunners.codecoverage.run_tests'
        elif options.get('figleaf'):
            test_runner_name = 'test_extensions.testrunners.figleafcoverage.run_tests'
        elif options.get('xml'):
            test_runner_name = 'test_extensions.testrunners.xmloutput.run_tests'
        else:
            test_runner_name = settings.TEST_RUNNER

        # skippers = options.get('skip').split(',')  #  TODO  complain if no args

        test_path = test_runner_name.split('.')
        # Allow for Python 2.5 relative paths
        if len(test_path) > 1:
            test_module_name = '.'.join(test_path[:-1])
        else:
            test_module_name = '.'
        test_module = __import__(test_module_name, {}, {}, test_path[-1])
        test_runner = getattr(test_module, test_path[-1])
        #print test_runner
        # print test_runner.__file__

        if hasattr(settings, 'SKIP_TESTS'):
            if not test_labels:
                test_labels = list()
                for app in get_apps():
                    test_labels.append(app.__name__.split('.')[-2])
            for app in settings.SKIP_TESTS:
                try:
                    test_labels.remove(app)
                except ValueError:
                    pass
        failures = test_runner(test_labels, verbosity=verbosity,
                                    interactive=interactive) # , skip_apps=skippers)
        if failures:
            sys.exit(failures)
