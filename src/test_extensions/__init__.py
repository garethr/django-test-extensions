import os
import sys
import traceback

from django.utils import autoreload

_mtimes = autoreload._mtimes
_win = autoreload._win
_code_changed = autoreload.code_changed
_error_files = []
def my_code_changed():
    global _mtimes, _win
    for filename in filter(lambda v: v, map(lambda m: getattr(m, "__file__", None), sys.modules.values())) + _error_files:
        if filename.endswith(".pyc") or filename.endswith(".pyo"):
            filename = filename[:-1]
        if not os.path.exists(filename):
            continue # File might be in an egg, so it can't be reloaded.
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes:
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes[filename]:
            _mtimes = {}
            try:
                del _error_files[_error_files.index(filename)]
            except ValueError: pass
            return True
    return False

def check_errors(fn):
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except (ImportError, IndentationError,
                NameError, SyntaxError, TypeError):
            et, ev, tb = sys.exc_info()

            if getattr(ev, 'filename', None) is None:
                # get the filename from the last item in the stack
                filename = traceback.extract_tb(tb)[-1][0]
            else:
                filename = ev.filename

            if filename not in _error_files:
                _error_files.append(filename)

            raise

    return wrapper

_main = autoreload.main
def my_main(main_func, args=None, kwargs=None):
    wrapped_main_func = check_errors(main_func)
    _main(wrapped_main_func, args=args, kwargs=kwargs)

autoreload.code_changed = my_code_changed
autoreload.main = my_main
