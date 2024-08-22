from rest_framework import serializers


class PaginatedSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField()
    previous = serializers.CharField()


class EnumFieldSerializer(serializers.ChoiceField):
    def __init__(self, enum, enum_use_values: bool = False, **kwargs):
        self.enum = enum
        self.enum_use_values = enum_use_values
        choices = [(tag.name, tag.value) for tag in self.enum]
        super().__init__(choices=choices, **kwargs)

    def to_representation(self, obj):
        if isinstance(obj, self.enum):
            return obj.value
        return super().to_representation(obj)

    def to_internal_value(self, data):
        try:
            return self.enum(data).value if self.enum_use_values else self.enum(data)
        except ValueError:
            self.fail("invalid_choice", input=data)
