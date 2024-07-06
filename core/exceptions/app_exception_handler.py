from typing import Union

from django.db import DatabaseError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .app_exceptions import AppExceptionCase


def exception_message(error_type: str, message: Union[str, list, dict, None]):
    """
    Exception message returned by the application when an error occurs
    :param error_type: the type of error
    :param message: the error message
    """
    return {
        "error_type": error_type,
        "error_message": message,
    }


def custom_exception_handler(exc, context):
    """
    The function handles custom exceptions by mapping them to specific
    handlers and returning a response with the appropriate status code and message.

    :param exc: The `exc` parameter is the exception object that was raised.
    It contains information about the exception, such as its type, message, and traceback
    :param context: The `context` parameter in the `custom_exception_handler` function
    is a dictionary that contains information about the current request and view that
    raised the exception.
    :return: a response object.
    """

    if isinstance(exc, exceptions.APIException):
        return http_exception_handler(exc)

    if isinstance(exc, DatabaseError):
        return db_exception_handler(exc)

    if isinstance(exc, AppExceptionCase):
        return app_exception_handler(exc)

    return exception_handler(exc, context)


def http_exception_handler(exc):
    """
    handle http exceptions raised by the application
    :param exc: the exception
    """
    return Response(
        data=exception_message(error_type="HttpException", message=exc.detail),
        status=exc.status_code,
    )


def db_exception_handler(exc):
    """
    handle database exceptions raised by the application
    :param exc: the exception
    """
    return Response(
        status=status.HTTP_400_BAD_REQUEST,
        data=exception_message(
            error_type="DatabaseException",
            message=exc.args[0],
        ),
    )


def app_exception_handler(exc):
    """
    handle any other exceptions raised by the application
    :param exc: the exception message
    """
    return Response(
        data=exception_message(
            error_type=exc.exception_case, message=exc.error_message
        ),
        status=exc.status_code,
    )
