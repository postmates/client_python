import logging

from .vendor import six

if six.PY3:
    import _thread as thread_module
else:
    import thread as thread_module
import time
import traceback

from . import (CollectorRegistry, multiprocess)
from .exposition import make_wsgi_app
from .multiprocess import archive_metrics


CLEANUP_INTERVAL = 5.0

registry = CollectorRegistry()
multiprocess.InMemoryCollector(registry)
app = make_wsgi_app(registry)
log = logging.getLogger(__name__)


def archive_thread():
    while True:
        log.info("startup")
        try:
            log.info("cleaning up")
            archive_metrics()
        except Exception:
            traceback.print_exc()
        time.sleep(CLEANUP_INTERVAL)


def start_archiver_thread():
    thread_module.start_new_thread(archive_thread, (), {})


# on_starting is a gunicorn-specific server hook
def on_starting(server):
    start_archiver_thread()
