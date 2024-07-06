from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.exceptions import AppException
from core.interfaces import CrudRepositoryInterface
from core.utils import CustomPageNumberPagination


class SqlBaseRepository(CrudRepositoryInterface):
    model: models.Model
    object_name: str

    def __init__(self):
        """
        Base class to be inherited by all sql repositories. This class comes with
        base crud functionalities attached

        :param model: base model of the class to be used for queries
        """
        self.custom_paginator = CustomPageNumberPagination()

    def index(self, paginate) -> [models.Model]:
        """
        :return: {list} returns a list of objects of type model
        """

        results = self.custom_paginator.paginate_queryset(
            self.model.objects.all(), paginate  # noqa
        )
        return self.custom_paginator, results

    def create(self, obj_data: dict) -> models.Model:
        """

        :param obj_data: the data you want to use to create the model
        :return: {object} - Returns an instance object of the model passed
        """

        model_obj = self.model(**obj_data)  # noqa
        model_obj.save()
        return model_obj

    def update_by_id(self, obj_id: str, obj_data: dict) -> models.Model:
        """
        :param obj_id: id of object to update
        :param obj_data: {dict} update data. This data will be used to update
        any object that matches the id specified
        :return: model_object - Returns an instance object of the model passed
        """
        assert obj_id, "update_by_id missing  obj_id of object to update"
        assert obj_data, "update_by_id missing update data of object"
        assert isinstance(obj_data, dict), "update_by_id parameters not a dict"

        db_obj = self.find_by_id(obj_id)
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        db_obj.save()
        return db_obj

    def update(self, filter_param: dict, obj_data: dict) -> models.Model:
        """
        :param filter_param {dict}. Parameters to be filtered by model object passed
        :param obj_data: {dict} update data. This data will be used to update
        any object that matches the filter_param specified
        :return: model_object - Returns an instance object of the model passed
        """
        db_obj = self.find(filter_param=filter_param)
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
            db_obj.save()
        return db_obj

    def find_by_id(self, obj_id: str) -> models.Model:
        """
        returns an object matching the specified id if it exists in the database
        :param obj_id: id of object to query
        """

        try:
            return self.model.objects.get(pk=obj_id)  # noqa
        except ObjectDoesNotExist:
            raise AppException.NotFoundException(
                error_message=f"{self.object_name}({obj_id}) does not exist"
            )

    def find(self, filter_param: dict) -> models.Model:
        """
        This method returns the first object that matches the query parameters specified
        :param filter_param {dict}. Parameters to be filtered by model object passed
        """
        assert filter_param, "find missing filter parameters"
        assert isinstance(filter_param, dict), "find filter parameters not a dict"

        try:
            return self.model.objects.filter(**filter_param).get()  # noqa
        except ObjectDoesNotExist:
            raise AppException.NotFoundException(
                error_message=f"{self.object_name}({filter_param}) does not exist"
            )

    def find_all(self, filter_param: dict) -> [models.Model]:
        """
        This method returns all objects that matches the query
        parameters specified
        :param filter_param {dict}. Parameters to be filtered by model object passed
        """
        assert filter_param, "find all missing filter parameters"
        assert isinstance(filter_param, dict), "find all filter parameters not a dict"

        return self.model.objects.filter(**filter_param)  # noqa

    def delete_by_id(self, obj_id: str) -> models.Model:
        """
        returns an object matching the specified obj_id if it exists in the database
        :param obj_id: id of object to delete
        """

        db_obj = self.find_by_id(obj_id)
        db_obj.delete()
        return db_obj

    def delete(self, filter_params: dict) -> models.Model:
        """
        :param filter_params:
        :return:
        """

        db_obj = self.find(filter_params)
        db_obj.delete()
        return db_obj
