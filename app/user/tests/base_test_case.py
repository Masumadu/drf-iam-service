from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from app.user.controller import UserController
from app.user.models import UserModel
from app.user.repository import UserRepository

from .test_data import UserTestData


class BaseTestCase(APITestCase):
    def setUp(self):
        self.setup_test_data()
        self.setup_patches()
        self.instantiate_classes()
        return None

    def setup_test_data(self):
        self.user_test_data = UserTestData()
        self.user_model = UserModel.objects.create(**self.user_test_data.existing_user)
        self.token = RefreshToken.for_user(self.user_model)
        self.access_token = str(self.token.access_token)
        self.refresh_token = str(self.token)
        self.content_type = "application/json"
        self.data_format = "json"
        self.request_url = "http://localhost"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def instantiate_classes(self):
        """This is where all classes are instantiated for the test"""
        self.user_repository = UserRepository()
        self.user_controller = UserController(user_repository=self.user_repository)

    def setup_patches(self):
        """This is where all mocked object are setup for the test"""
        self.request_factory = APIRequestFactory()
