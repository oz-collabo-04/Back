from rest_framework import serializers

from chat.models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"

    def validate(self, data):
        # 유저와 전문가 각각 유효성 검사 수행
        self.validate_user(data)
        self.validate_expert(data)
        self.validate_user_and_expert(data)
        return data

    def validate_user(self, data):
        # 유효성 검사에서 data가 딕셔너리인지 확인
        if isinstance(data, dict):
            user = data.get("user")
        else:
            user = data  # 이미 객체인 경우

        if not user:
            raise serializers.ValidationError("User 정보가 필요합니다.")
        return user

    def validate_expert(self, data):
        expert = data.get("expert")
        if not expert:
            raise serializers.ValidationError("전문가 정보는 필수입니다.")

    def validate_user_and_expert(self, data):
        user = data.get("user")
        expert = data.get("expert")
        if user == expert:
            raise serializers.ValidationError("유저와 전문가는 동일할 수 없습니다.")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, data):
        if "content" not in data or not data["content"].strip():
            raise serializers.ValidationError("메시지 내용은 필수입니다.")
        return data
