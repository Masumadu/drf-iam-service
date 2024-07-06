from rest_framework import serializers

from app.user.serializer import UserSerializer
from core.serializers import PaginatedSerializer


class TodoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    todo = serializers.CharField()
    completed = serializers.BooleanField()
    user = UserSerializer()


class PaginatedTodoSerializer(PaginatedSerializer):
    results = TodoSerializer(many=True)


class CreateTodoSerializer(serializers.Serializer):
    todo = serializers.CharField(required=True)


class UpdateTodoSerializer(serializers.Serializer):
    todo = serializers.CharField(required=False)
    completed = serializers.BooleanField(required=False)
    user_id = serializers.UUIDField(required=False)


class TodoQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=50)
