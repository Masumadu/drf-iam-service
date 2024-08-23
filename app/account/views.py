import pinject
from django.shortcuts import render
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.request import Request
from rest_framework.response import Response

from core.services import KeycloakAuthService
from core.utils import (
    IsSuperAdmin,
    KeycloakAuthentication,
    api_responses,
)

from .controller import AccountController
from .repository import AccountRepository
from .serializer import (
    AccountQuerySerializer,
    AccountSerializer,
    AuthTokenSerializer,
    ChangeAccountPasswordSerializer,
    ConfirmOtpResponseSerializer,
    ConfirmOtpSerializer,
    CreateAccountSerializer,
    GenerateApiKeySerializer,
    LoginAccountSerializer,
    PaginatedAccountSerializer,
    RefreshTokenSerializer,
    ResetAccountPasswordSerializer,
    UpdateAccountGroupSerializer,
)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[AccountController, AccountRepository, KeycloakAuthService],
)
account_controller: AccountController = obj_graph.provide(AccountController)
api_doc_tag = ["Account"]


@extend_schema(
    responses=api_responses(status_codes=[200], schema=PaginatedAccountSerializer),
    tags=api_doc_tag,
    parameters=[AccountQuerySerializer],
)
@api_view(http_method_names=["GET"])
@authentication_classes([KeycloakAuthentication])
@permission_classes([IsSuperAdmin])
def view_all_accounts(request):
    return account_controller.view_all_accounts(request)


@extend_schema(
    responses=api_responses(status_codes=[200, 401, 404], schema=AccountSerializer),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@authentication_classes([KeycloakAuthentication])
def get_account(request):
    serializer = account_controller.get_account(request)
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=CreateAccountSerializer,
    responses=api_responses(
        status_codes=[201, 400, 409, 422, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def create_account(request: Request):
    serializer = account_controller.create_account(
        request.data,
        f"{request.scheme}://{request.get_host()}{reverse('verify_account_email')}",
    )
    return Response(data=serializer.data, status=201)


@extend_schema(
    responses=api_responses(status_codes=[200], schema=AuthTokenSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["GET"])
def verify_account_email(request: Request):
    token = request.query_params.get("token")
    if result := account_controller.verify_account_email(token):
        return render(
            request,
            "email/email_verification_success.html",
            {"email": result.email},
        )
    return render(request, "email/expired_email_verification.html")


@extend_schema(
    responses=api_responses(
        status_codes=[200, 401, 404, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@authentication_classes([KeycloakAuthentication])
def resend_email_verification(request: Request):
    serializer = account_controller.send_account_verification_link(
        request.user.id,
        f"{request.scheme}://{request.get_host()}{reverse('verify_account_email')}",
    )
    return Response(data=serializer.data, status=200)


@extend_schema(
    responses=api_responses(
        status_codes=[200, 401, 404], schema=GenerateApiKeySerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@authentication_classes([KeycloakAuthentication])
def generate_apikey(request: Request):
    result = account_controller.generate_account_apikey(request)
    return Response(data=result, status=200)


@extend_schema(
    request=AccountSerializer,
    responses=api_responses(status_codes=[200, 404], schema=AccountSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["GET"])
def get_account_by_apikey(request: Request, apikey: str):
    serializer = account_controller.get_account_by_apikey(apikey)
    return Response(data=serializer.data, status=200)


@extend_schema(
    responses=api_responses(status_codes=[200, 400, 401], schema=AccountSerializer),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@authentication_classes([KeycloakAuthentication])
def toggle_apikey_status(request: Request):
    serializer = account_controller.toggle_account_apikey_status(request)
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=LoginAccountSerializer,
    responses=api_responses(
        status_codes=[200, 400, 422, 500], schema=AuthTokenSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def login_account(request):
    result = account_controller.login_account(request)
    return Response(data=result, status=200)


@extend_schema(
    request=RefreshTokenSerializer,
    responses=api_responses(status_codes=[200, 422, 500], schema=AuthTokenSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def refresh_access_token(request):
    result = account_controller.refresh_user_token(request)
    return Response(data=result, status=200)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="email",
            location=OpenApiParameter.QUERY,
            description="account's email",
            required=False,
            type=str,
        )
    ],
    responses=api_responses(
        status_codes=[200, 400, 404, 422, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["GET"])
def reset_password_request(request: Request):
    serializer = account_controller.reset_account_password_request(
        email=request.query_params.get("email")
    )
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=ResetAccountPasswordSerializer,
    responses=api_responses(
        status_codes=[204, 400, 404, 422, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def reset_password(request: Request):
    serializer = account_controller.reset_account_password(request)
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=ChangeAccountPasswordSerializer,
    responses=api_responses(
        status_codes=[200, 400, 401, 422, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["POST"])
@authentication_classes([KeycloakAuthentication])
def change_password(request):
    result = account_controller.change_account_password(request)
    return Response(data=result, status=200)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="email",
            location=OpenApiParameter.QUERY,
            description="email to receive otp on",
            required=False,
            type=str,
        )
    ],
    responses=api_responses(
        status_codes=[200, 400, 404, 500], schema=AccountSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["GET"])
def send_one_time_password(request: Request):
    serializer = account_controller.send_otp(email=request.query_params.get("email"))
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=ConfirmOtpSerializer,
    responses=api_responses(
        status_codes=[202, 400, 422], schema=ConfirmOtpResponseSerializer
    ),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def confirm_one_time_password(request):
    result = account_controller.otp_confirmation(request)
    return Response(data=result, status=200)


@extend_schema(
    responses=api_responses(status_codes=[204, 401, 404], schema=None), tags=api_doc_tag
)
@api_view(http_method_names=["DELETE"])
@authentication_classes([KeycloakAuthentication])
def deactivate_account(request):
    result = account_controller.deactivate_account(request)
    return Response(data=result, status=204)


@extend_schema(
    request=UpdateAccountGroupSerializer,
    responses=api_responses(
        status_codes=[200, 401, 404, 422], schema=AccountSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["PATCH"])
@authentication_classes([KeycloakAuthentication])
@permission_classes([IsSuperAdmin])
def update_account_group(request):
    serializer = account_controller.update_group(request)
    return Response(data=serializer.data, status=200)
