import secrets
from datetime import datetime, timedelta, timezone
from random import choices
from string import digits

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.core.cache import cache
from jwt.exceptions import PyJWTError
from rest_framework.request import Request

from core.constants import AccountStatusEnum, GroupEnum
from core.exceptions import AppException
from core.interfaces.notifications import Notifier
from core.notifications import (
    EmailNotificationHandler,
    SMSNotificationHandler,
)
from core.services import KeycloakAuthService
from core.utils import remove_none_fields

from .models import AccountModel
from .repository import AccountRepository
from .serializer import (
    AccountSerializer,
    ChangeAccountPasswordSerializer,
    ConfirmOtpSerializer,
    CreateAccountSerializer,
    LoginAccountSerializer,
    RefreshTokenSerializer,
    ResetAccountPasswordSerializer,
    UpdateAccountGroupSerializer,
)


class AccountController(Notifier):
    def __init__(
        self,
        account_repository: AccountRepository,
        keycloak_auth_service: KeycloakAuthService,
    ):
        self.account_repository = account_repository
        self.keycloak_auth_service = keycloak_auth_service
        self.otp_code_key = "{account_id}_otp_code"
        self.sec_code_key = "{account_id}_sec_code"

    def view_all_accounts(self, request):
        paginator, accounts = self.account_repository.index(request)
        serializer = AccountSerializer(accounts, many=True)
        return paginator.get_paginated_response(serializer.data)

    def get_account(self, request):
        return AccountSerializer(self.account_repository.find_by_id(request.user.id))

    def create_account(self, obj_data: dict, verification_url: str):
        serializer = CreateAccountSerializer(data=obj_data)
        if serializer.is_valid():
            data = serializer.data
            data["status"] = AccountStatusEnum.inactive.value
            account = self.account_repository.create(data)
            iam_account_id = self.keycloak_auth_service.create_user(
                obj_data={
                    "username": str(account.id),
                    "password": obj_data.get("password"),
                    "email": data.get("email"),
                }
            )
            updated_account = self.account_repository.update_by_id(
                obj_id=account.id, obj_data={"iam_provider_id": iam_account_id}
            )
            self.send_otp(phone=account.phone)
            self.send_account_verification_link(
                user_id=str(account.id),
                url=verification_url,
            )
            updated_account.groups.add(Group.objects.get(name=GroupEnum.user.value))
            return AccountSerializer(updated_account)
        raise AppException.ValidationException(error_message=serializer.errors)

    def send_account_verification_link(self, user_id: str, url: str):
        account = self.account_repository.find_by_id(user_id)
        if account.is_email_verified:
            raise AppException.BadRequestException(
                error_message="email already verified"
            )
        token = self.generate_token(
            payload={
                "id": str(account.id),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            }
        )
        self._send_email(
            obj_data={
                "email": account.email,
                "template_name": "email_verification.html",
                "metadata": {
                    "user_id": str(account.id),
                    "email": account.email,
                    "verification_link": f"{url}?token={token}",
                    "subject": "Verify Account Email",
                },
            }
        )
        return AccountSerializer(account)

    def generate_token(self, payload: dict) -> str:
        return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")

    def verify_account_email(self, token: str):
        try:
            payload: dict = self.decode_token(token)
            return self.account_repository.update_by_id(
                obj_id=payload.get("id"), obj_data={"is_email_verified": True}
            )
        except (AppException.BadRequestException, AppException.NotFoundException):
            return None

    def decode_token(self, token: str) -> dict:
        try:
            payload: dict = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=settings.JWT_ALGORITHMS,
            )
            return payload
        except PyJWTError as exc:
            raise AppException.BadRequestException(error_message=exc.args) from exc

    def verify_account_phone(self, request: Request):
        account = self.account_repository.find_by_id(request.user.id)
        otp_confirmation = self.confirm_otp(
            account_id=str(account.id),
            otp_code=request.query_params.get("verification_code"),
        )
        self._confirm_sec_code(
            account_id=otp_confirmation.get("id"),
            sec_code=otp_confirmation.get("sec_code"),
        )
        account = self.account_repository.update_by_id(
            obj_id=account.id, obj_data={"is_phone_verified": True}
        )
        return AccountSerializer(account)

    def generate_account_apikey(self, request) -> dict:
        key = "".join(
            char for char in secrets.token_urlsafe(32) if char not in ["-", "_"]
        )
        self.account_repository.update_by_id(
            obj_id=str(request.user.id),
            obj_data={
                "api_key": AccountModel.hash_apikey(value=key),
                "api_key_enabled": True,
            },
        )
        return {"apikey": key, "is_active": True}

    def get_account_by_apikey(self, apikey: str):
        account = self.account_repository.find(
            filter_param={"api_key": AccountModel.hash_apikey(value=apikey)}
        )
        return AccountSerializer(account)

    def toggle_account_apikey_status(self, request):
        account = self.account_repository.find_by_id(request.user.id)
        if not account.api_key:
            raise AppException.BadRequestException(error_message="apikey not available")
        apikey_status = not account.api_key_enabled
        update_account = self.account_repository.update_by_id(
            obj_id=account.id, obj_data={"api_key_enabled": apikey_status}
        )
        return AccountSerializer(update_account)

    def login_account(self, request):
        serializer = LoginAccountSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if account := authenticate(
                request=request,
                username=data.get("username"),
                password=data.get("password"),
            ):
                self.is_account_in_iam(account=account, password=data.get("password"))
                iam_token = self.keycloak_auth_service.get_token(
                    obj_data={
                        "username": str(account.id),
                        "password": data.get("password"),
                    }
                )
                self.account_repository.update(
                    filter_param={"username": data.get("username")},
                    obj_data={"last_login": datetime.now(timezone.utc)},
                )
                return iam_token
            raise AppException.BadRequestException(
                error_message="username or password invalid"
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def is_account_in_iam(self, account, password: str):
        if not account.iam_provider_id:
            iam_account_id = self.keycloak_auth_service.create_user(
                obj_data={
                    "username": str(account.id),
                    "password": password,
                    "email": account.email,
                }
            )
            return self.account_repository.update_by_id(
                obj_id=account.id, obj_data={"iam_provider_id": iam_account_id}
            )
        return account

    def refresh_user_token(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            return self.keycloak_auth_service.refresh_token(
                refresh_token=serializer.validated_data.get("refresh_token")
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def reset_account_password_request(self, email: str, phone: str):
        account = self.account_repository.find(
            remove_none_fields({"email": email, "phone": phone})
        )
        self.send_otp(phone=phone, email=email)
        return AccountSerializer(account)

    def reset_account_password(self, request: Request):
        serializer = ResetAccountPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            self._confirm_sec_code(
                account_id=data.get("id"), sec_code=data.get("sec_code")
            )
            account = self.account_repository.update_by_id(
                obj_id=data.get("id"), obj_data={"secret": data.get("new_password")}
            )
            self.keycloak_auth_service.change_password(
                obj_data={
                    "iam_user_id": account.iam_provider_id,
                    "password": data.get("new_password"),
                }
            )
            self._send_email(
                obj_data={
                    "email": account.email,
                    "template_name": "account_password_reset.html",
                    "metadata": {
                        "user_id": str(account.id),
                        "email": account.email,
                        "subject": "Reset Account Password",
                    },
                }
            )
            return AccountSerializer(account)
        raise AppException.ValidationException(error_message=serializer.errors)

    def change_account_password(self, request):
        serializer = ChangeAccountPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if authenticate(
                request=request,
                username=request.user.username,
                password=data.get("old_password"),
            ):
                request.user.set_password(data.get("new_password"))
                request.user.save()
                self.keycloak_auth_service.change_password(
                    obj_data={
                        "iam_user_id": request.user.iam_provider_id,
                        "password": data.get("new_password"),
                    }
                )
                return self.keycloak_auth_service.get_token(
                    obj_data={
                        "username": str(request.user.id),
                        "password": data.get("new_password"),
                    }
                )
            raise AppException.BadRequestException(
                error_message="username or password invalid"
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def send_otp(self, phone: str = None, email: str = None):
        filter_param: dict = remove_none_fields({"email": email, "phone": phone})
        if not filter_param:
            raise AppException.BadRequestException(error_message="invalid otp channel")
        account = self.account_repository.find(filter_param)
        if phone:
            self._sms_otp(account_id=str(account.id), phone_number=account.phone)
        if email:
            self._email_otp(account_id=str(account.id), email=account.email)
        return AccountSerializer(account)

    def otp_confirmation(self, request):
        serializer = ConfirmOtpSerializer(data=request.data)
        if serializer.is_valid():
            return self.confirm_otp(
                account_id=serializer.validated_data.get("id"),
                otp_code=serializer.validated_data.get("otp_code"),
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def confirm_otp(self, account_id: str, otp_code: str) -> dict:
        result = cache.get(self.otp_code_key.format(account_id=account_id))
        if not result:
            raise AppException.BadRequestException(error_message="otp code has expired")
        if otp_code != result and otp_code not in settings.MASTER_OTP_CODES:
            raise AppException.BadRequestException(error_message="invalid otp code")
        sec_code: str = self._create_sec_code_record(
            account_id=account_id,
            sec_code=self._generate_security_code(length=16),
            code_expiration=5,
        )
        cache.delete(self.otp_code_key.format(account_id=account_id))
        return {"id": account_id, "sec_code": sec_code}

    def _sms_otp(self, account_id: str, phone_number: str):
        otp_code: str = self._generate_otp_code(length=6)
        self._create_otp_record(
            account_id=account_id, otp_code=otp_code, code_expiration=5
        )
        self._send_sms(
            obj_data={
                "phone": phone_number,
                "template_name": "account_otp_code.txt",
                "metadata": {
                    "user_id": account_id,
                    "otp": otp_code,
                },
            }
        )
        return None

    def _email_otp(self, account_id: str, email: str):
        otp_code: str = self._generate_otp_code(length=6)
        self._create_otp_record(
            account_id=account_id, otp_code=otp_code, code_expiration=5
        )
        self._send_email(
            obj_data={
                "email": email,
                "template_name": "account_otp_code.html",
                "metadata": {
                    "account_id": account_id,
                    "email": email,
                    "otp": otp_code,
                    "subject": "One-Time Password (OTP) Verification",
                },
            }
        )
        return None

    def _confirm_sec_code(self, account_id: str, sec_code: str) -> str:
        result = cache.get(self.sec_code_key.format(account_id=account_id))
        if not result:
            raise AppException.BadRequestException(
                error_message="security code has expired"
            )
        if sec_code != result:
            raise AppException.BadRequestException(
                error_message="security code is invalid"
            )
        cache.delete(self.sec_code_key.format(account_id=account_id))
        return result

    def _create_otp_record(self, account_id: str, otp_code: str, code_expiration: int):
        return cache.set(
            self.otp_code_key.format(account_id=account_id),
            otp_code,
            timeout=60 * code_expiration,
        )

    def _create_sec_code_record(
        self, account_id: str, sec_code: str, code_expiration: int
    ):
        result = cache.get(self.sec_code_key.format(account_id=account_id))
        if not result:
            cache.set(
                self.sec_code_key.format(account_id=account_id),
                sec_code,
                timeout=60 * code_expiration,
            )
            return sec_code
        return result

    def _generate_otp_code(self, length: int) -> str:
        return "".join(choices(digits, k=length))

    # noinspection PyMethodMayBeStatic
    def _generate_security_code(self, length: int) -> str:
        return secrets.token_urlsafe(length)

    def deactivate_account(self, request):
        self.account_repository.update_by_id(
            obj_id=request.user.id,
            obj_data={
                "is_deleted": True,
                "deleted_by": request.user.id,
                "deleted_at": datetime.now(timezone.utc),
                "is_active": False,
                "status": AccountStatusEnum.deactivated.value,
            },
        )
        return None

    def _send_sms(self, obj_data: dict):
        self.notify(
            SMSNotificationHandler(
                recipients=obj_data.get("phone"),
                template_name=obj_data.get("template_name"),
                metadata=obj_data.get("metadata"),
            )
        )
        return None

    def _send_email(self, obj_data: dict):
        self.notify(
            EmailNotificationHandler(
                recipients=obj_data.get("email"),
                template_name=obj_data.get("template_name"),
                metadata=obj_data.get("metadata"),
            )
        )
        return None

    def update_group(self, request):
        serializer = UpdateAccountGroupSerializer(data=request.data)
        if serializer.is_valid():
            account = self.account_repository.find_by_id(
                obj_id=serializer.validated_data.get("id")
            )
            account.groups.add(
                Group.objects.get(name=serializer.validated_data.get("group"))
            )
            return AccountSerializer(account)
        raise AppException.ValidationException(error_message=serializer.errors)
