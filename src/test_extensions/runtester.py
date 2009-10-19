from django.core.management.base import BaseCommand, CommandError
from django.utils import autoreload
from optparse import make_option
import os
import sys
import time
import traceback

INPROGRESS_FILE = 'testing.inprogress'

def get_test_command():
    """
    Return an instance of the Command class to use.

    This method can be patched in to run a test command other than the on in
    core Django.  For example, to make a runtester for South:

    from django.core.management.commands import runtester
    from django.core.management.commands.runtester import Command

    def get_test_command():
        from south.management.commands.test import Command as TestCommand
        return TestCommand()

    runtester.get_test_command = get_test_command
    """

    from django.core.management.commands.test import Command as TestCommand
    return TestCommand()

def my_reloader_thread():
    """
    Wait for a test run to complete before exiting.
    """

    # If a file is saved while tests are being run, the base reloader just
    # kills the process.  This is bad because it wedges the database and then
    # the user is prompted to delete the database.  Instead, wait for
    # INPROGRESS_FILE to disappear, then exit.  Exiting the thread will then
    # rerun the suite.
    while autoreload.RUN_RELOADER:
        if autoreload.code_changed():
            while os.path.exists(INPROGRESS_FILE):
                time.sleep(1)
            sys.exit(3) # force reload
        time.sleep(1)

# monkeypatch the reloader_thread function with the one above
autoreload.reloader_thread = my_reloader_thread

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = "Starts a command that tests upon saving files."
    args = '[optional apps to test]'

    # Validation is called explicitly each time the suite is run
    requires_model_validation = False

    def handle(self, *args, **options):
        if os.path.exists(INPROGRESS_FILE):
            os.remove(INPROGRESS_FILE)

        def inner_run():
            try:
                open(INPROGRESS_FILE, 'wb').close()

                test_command = get_test_command()
                test_command.handle(*args, **options)
            finally:
                if os.path.exists(INPROGRESS_FILE):
                    os.remove(INPROGRESS_FILE)

        autoreload.main(inner_run)
