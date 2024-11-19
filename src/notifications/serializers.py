from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def validate(self, data):
        # 제목 길이 검증
        if 'title' in data and len(data['title']) > 20:
            raise serializers.ValidationError("제목은 20자를 초과할 수 없습니다.")
        # 내용 길이 검증
        if 'message_id' in data and len(data['message_id']) > 100:
            raise serializers.ValidationError("내용은 100자를 초과할 수 없습니다.")
        return data