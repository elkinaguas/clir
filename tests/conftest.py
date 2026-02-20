import os
import shutil
import tempfile


_ORIGINAL_HOME = os.environ.get("HOME")
_TEST_HOME = tempfile.mkdtemp(prefix="clir-test-home-")
os.environ["HOME"] = _TEST_HOME


def pytest_sessionfinish(session, exitstatus):
    if _ORIGINAL_HOME is None:
        os.environ.pop("HOME", None)
    else:
        os.environ["HOME"] = _ORIGINAL_HOME

    shutil.rmtree(_TEST_HOME, ignore_errors=True)
