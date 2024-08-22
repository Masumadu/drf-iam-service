import logging
from logging.handlers import SMTPHandler
from threading import Thread


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return f"{module}.{obj.__class__.__name__}"


def get_error_context(
    module, method, error, calling_method=None, calling_module=None, exc_class=None
):
    return {
        "exception_class": exc_class,
        "module": module,
        "method": method,
        "calling module": calling_module,
        "calling method": calling_method,
        "error": error,
    }


class MailHandler(SMTPHandler):
    def emit(self, record):
        """
        Emit a record.
        Format the record and send it to the specified addressees.
        """
        Thread(target=self.send_mail, kwargs={"record": record}).start()

    def send_mail(self, record):
        self.timeout = 30
        super().emit(record)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)
