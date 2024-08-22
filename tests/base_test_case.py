from unittest import mock

from rest_framework.test import APIRequestFactory, APITestCase


class BaseTestCase(APITestCase):
    def setUp(self):
        self.setup_test_data()
        self.setup_patches()
        self.instantiate_classes()

    def setup_test_data(self):
        self.access_token = "lskjasljdlajdlfakjlakjlajf"
        self.refresh_token = self.access_token
        self.content_type = "application/json"
        self.data_format = "json"
        self.request_url = "http://localhost"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def instantiate_classes(self):
        """This is where all classes are instantiated for the test"""

    def setup_patches(self):
        """This is where all mocked object are setup for the test"""
        self.request_factory = APIRequestFactory()
        kafka_email_ = mock.patch(
            "core.notifications.email_notification_handler.publish_to_kafka"
        )
        self.addCleanup(kafka_email_.stop)
        self.kafka_email = kafka_email_.start()
        kafka_sms_ = mock.patch(
            "core.notifications.sms_notification_handler.publish_to_kafka"
        )
        self.addCleanup(kafka_sms_.stop)
        self.kafka_sms = kafka_sms_.start()
