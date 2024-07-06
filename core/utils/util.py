from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)
from rest_framework.pagination import PageNumberPagination

from core.exceptions import AppException, exception_message


def api_responses(status_codes: list, schema: Any):
    responses = {}
    over_all_exceptions = {
        400: OpenApiResponse(
            description="exception caused by invalid client requests",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.BadRequestException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.BadRequestException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        401: OpenApiResponse(
            description="exception caused by unauthenticated client requests",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.UnauthorizedException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.UnauthorizedException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        403: OpenApiResponse(
            description="exception caused by limited client permissions",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.PermissionException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.UnauthorizedException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        404: OpenApiResponse(
            description="exception caused by resource nonexistence on server",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.NotFoundException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.NotFoundException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        409: OpenApiResponse(
            description="exception caused by resource duplication on server",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.ResourceExistException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.ResourceExistException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        422: OpenApiResponse(
            description="exception caused by invalid client request data",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.ValidationException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.ValidationException.__name__,
                        message={"email": ["Enter a valid email address."]},
                    ),
                ),
            ],
        ),
        500: OpenApiResponse(
            description="exception caused by servers inability to process client request",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.InternalServerException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.InternalServerException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
        503: OpenApiResponse(
            description="exception caused by servers inability to access third party services",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    f"{AppException.ServiceUnavailableException.__name__} Response",
                    value=exception_message(
                        error_type=AppException.ServiceUnavailableException.__name__,
                        message="error message",
                    ),
                ),
            ],
        ),
    }
    for code in status_codes:
        if not over_all_exceptions.get(code):
            responses[code] = OpenApiResponse(
                description="successful response", response=schema
            )
        else:
            responses[code] = over_all_exceptions.get(code)
    return responses


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100
