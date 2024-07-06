import abc


class CrudRepositoryInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "index"))
            and callable(subclass.index)
            and hasattr(subclass, "create")
            and callable(subclass.create)
            and hasattr(subclass, "update_by_id")
            and callable(subclass.update_by_id)
            and hasattr(subclass, "update")
            and callable(subclass.update)
            and hasattr(subclass, "find_by_id")
            and callable(subclass.find_by_id)
            and hasattr(subclass, "find")
            and callable(subclass.find)
            and hasattr(subclass, "find_all")
            and callable(subclass.find_all)
            and hasattr(subclass, "delete_by_id")
            and callable(subclass.delete_by_id)
            and hasattr(subclass, "delete")
            and callable(subclass.delete)
        )

    @abc.abstractmethod
    def index(self, *args):
        """
        when inherited, index should show all data belonging to a model
        :return: list of model objects of database records
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, obj_data):
        """
        when inherited, creates a new record
        :param obj_data: the data you want to use to create the model
        :return: a model object of created database record
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_by_id(self, obj_id, obj_data):
        """
        when inherited, updates a record by taking in the id, and the data you
        want to update with
        :param obj_id:
        :param obj_data:
        :return: a model object of updated database record
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update(self, filter_param, obj_data):
        """
        when inherited, updates a record by filtering with filter_param,
        and update with obj_data
        :param filter_param:
        :param obj_data:
        :return: a model object of updated database record
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, obj_id):
        """
        when inherited, finds a record by id
        :param obj_id:
        :return: a model object of a database record
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find(self, filter_param):
        """
        when inherited, finds a record by filtering with param
        :param filter_param:
        :return: a model object of a database record
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find_all(self, filter_param):
        """
        when inherited, finds a record by filtering with param
        :param filter_param:
        :return: a list of model objects of database records
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_id(self, obj_id):
        """
        when inherited, deletes a record by id
        :param obj_id:
        :return: a model object of deleted record
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, filter_param: dict):
        """
        when inherited, deletes a record by filtering with filter_param
        :param filter_param:
        :return: a model object of deleted record
        """

        raise NotImplementedError
