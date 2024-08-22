import abc


class AuthenticationInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_token")
            and callable(subclass.get_token)
            and hasattr(subclass, "refresh_token")
            and callable(subclass.refresh_token)
            and hasattr(subclass, "create_user")
            and callable(subclass.create_user)
            and hasattr(subclass, "update_user")
            and callable(subclass.update_user)
            and hasattr(subclass, "delete_user")
            and callable(subclass.delete_user)
            and hasattr(subclass, "change_password")
            and callable(subclass.change_password)
        )

    @abc.abstractmethod
    def get_token(self, request_data):
        """
        :param request_data: authentication data needed to retrieve valid token
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_token(self, request_data):
        """
        :param request_data: refresh token needed to get the next valid token
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_user(self, request_data):
        """
        :param request_data: data to create user with
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def change_password(self, request_data):
        """
        :param request_data: data to create user with
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update_user(self, request_data):
        """
        :param request_data: data to update user with
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete_user(self, request_data):
        """
        :param request_data: data to delete user with
        :return:
        """

        raise NotImplementedError
