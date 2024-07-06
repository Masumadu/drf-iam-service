import logging
from typing import Any

# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


class AppExceptionCase(Exception):
    """
    base exception to be raised by the application
    """

    def __init__(self, status_code: int, error_message: Any, context=None):
        """
        :param status_code: the http code return from request
        :param error_message: the message return from request
        :param context: other message suitable for troubleshooting errors
        """
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.error_message = error_message
        self.context = context
        logger.critical(self.context) if self.context else None

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code = {self.status_code} - error_message = {self.error_message}>"
        )


class AppException:
    """
    the various exceptions that will be raised by the application
    """

    class BadRequestException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by invalid requests
            """
            status_code = 400
            super().__init__(status_code, error_message, context)

    class InternalServerException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by servers inability to process a request
            """
            status_code = 500
            super().__init__(status_code, error_message, context)

    class ResourceExistException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by resource duplication
            """
            status_code = 409
            super().__init__(status_code, error_message, context)

    class NotFoundException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by resource nonexistence
            """
            status_code = 404
            super().__init__(status_code, error_message, context)

    class UnauthorizedException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by unauthenticated requests
            """
            status_code = 401
            super().__init__(status_code, error_message, context)

    class PermissionException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by limited permissions
            """
            status_code = 403
            super().__init__(status_code, error_message, context)

    class ValidationException(AppExceptionCase):
        """
        exception the catch errors caused by invalid request data
        """

        def __init__(self, error_message, context=None):
            status_code = 422
            super().__init__(status_code, error_message, context)

    class ServiceUnavailableException(AppExceptionCase):
        def __init__(self, error_message, context=None):
            """
            exception to catch errors caused by servers inability to access third party
            services
            """
            status_code = 503
            super().__init__(status_code, error_message, context)
