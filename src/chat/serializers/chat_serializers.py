from rest_framework import serializers

from chat.models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

    def validate(self, data):
        if 'user' not in data or 'expert' not in data:
            raise serializers.ValidationError("유저와 전문가 정보는 필수입니다.")
        if data['user'] == data['expert']:
            raise serializers.ValidationError("유저와 전문가는 동일할 수 없습니다.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    def validate(self, data):
        if 'content' not in data or not data['content'].strip():
            raise serializers.ValidationError("메시지 내용은 필수입니다.")
        return data