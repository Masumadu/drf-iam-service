from typing import List, Union

from django.conf import settings
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string

from core.exceptions import AppException
from core.interfaces import NotificationInterface
from core.producer import publish_to_kafka


class SMSNotificationHandler(NotificationInterface):
    def __init__(
        self,
        recipients: Union[str, List[str]],
        template_name: str = None,
        metadata: dict = None,
        plain_text: str = None,
    ):
        self.recipients: list = recipients
        self.template = template_name
        self.plain_text = plain_text
        self.metadata = metadata or {}
        # self.jinja2_environment = Jinja2Environment(
        #     loader=FileSystemLoader(
        #         searchpath=create_directory(
        #             path=settings.upload_directory, dir_name="templates/sms"
        #         )
        #     )
        # )

    def send(self) -> None:
        """
        Send SMS notification.
        """
        data = {
            "user_id": "salkjfda",
            "recipients": self._recipients(),
            "sender": settings.SMS_SENDER,
            "message": self.plain_text or self.message(),
        }
        publish_to_kafka(topic=settings.KAFKA_SMS_TOPIC, value=data)
        return None

    def message(self):
        try:
            if self.template:
                return render_to_string(f"sms/{self.template}", self.metadata)
            return None
            # return template.render(**self.metadata)
        except TemplateDoesNotExist as exc:
            raise AppException.InternalServerException(
                error_message=f"template{self.template, exc}"
            ) from exc

    def _recipients(self):
        if not isinstance(self.recipients, list):
            return [self.recipients]
        return self.recipients
