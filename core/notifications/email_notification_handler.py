from typing import List, Union

from django.conf import settings
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string

from core.exceptions import AppException
from core.interfaces.notifications import NotificationInterface
from core.producer import publish_to_kafka


class EmailNotificationHandler(NotificationInterface):
    def __init__(
        self,
        recipients: Union[str, List[str]],
        template_name: Union[str, None],
        metadata: dict = None,
        plain_text: str = None,
    ):
        self.recipients = recipients
        self.template = template_name
        self.plain_text = plain_text
        self.metadata = metadata or {}

    def send(self) -> None:
        """
        Send the email notification.
        """
        data = {
            "user_id": "alskdjfa",
            "sender": settings.SERVER_EMAIL,
            "subject": self.metadata.get("subject"),
            "recipients": self._recipients(),
            "html_body": self.html_text(),
            "text_body": self.plain_text,
        }
        publish_to_kafka(topic=settings.KAFKA_EMAIL_TOPIC, value=data)
        return None

    def html_text(self):
        try:
            if self.template:
                return render_to_string(f"email/{self.template}", self.metadata)
            return None
        except TemplateDoesNotExist as exc:
            raise AppException.InternalServerException(
                error_message=f"template{self.template, exc}"
            )

    def _recipients(self):
        if not isinstance(self.recipients, list):
            return [self.recipients]
        return self.recipients
