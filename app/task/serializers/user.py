from case.serializers import UserSerializer


class TaskListUserSerializer(UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        read_only_fields = UserSerializer.Meta.read_only_fields
        fields = (
            "id",
            "full_name",
            "url",
        )
