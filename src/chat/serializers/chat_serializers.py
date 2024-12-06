from rest_framework import serializers

from chat.models import ChatRoom, Message
from estimations.serializers.guest_seriailzers import EstimationsRequestSerializer
from reservations.seriailzers import ExpertInfoSerializer
from users.serializers.user_serializers import UserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    expert = ExpertInfoSerializer(read_only=True)
    request = EstimationsRequestSerializer(read_only=True)
    expert_id = serializers.IntegerField(write_only=True)
    request_id = serializers.IntegerField(write_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "user",
            "expert",
            "expert_id",
            "request",
            "request_id",
            "expert_exist",
            "user_exist",
            "last_message",
        ]
        read_only_fields = ["id", "user", "expert", "request", "expert_exist", "user_exist", "last_message"]

    def get_last_message(self, obj):
        last_chat = obj.message_set.order_by("-timestamp").first()
        if last_chat:
            return last_chat.content
        return ""


class ChatroomUpdateSerializer(serializers.ModelSerializer):
    user_exist = serializers.BooleanField(required=False)
    expert_exist = serializers.BooleanField(required=False)

    class Meta:
        model = ChatRoom
        fields = ["id", "user", "expert", "request", "expert_exist", "user_exist"]
        read_only_fields = ["id", "user", "expert", "request"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, data):
        if "content" not in data or not data["content"].strip():
            raise serializers.ValidationError("메시지 내용은 필수입니다.")
        return data
