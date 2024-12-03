import urllib.parse

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "gender", "phone_number", "profile_image", "prefer_service", "prefer_location"]
        read_only_fields = ("id", "email")

    def get_profile_image(self, obj):
        """
        profile_image 필드가 URL 형식인지 확인하고, 디코딩 후 /media/ 제거 및 :/를 ://로 수정.
        """
        if obj.profile_image:
            # URL 디코딩 처리
            decoded_url = urllib.parse.unquote(obj.profile_image.url)

            # "/media/" 제거
            if decoded_url.startswith("/media/"):
                decoded_url = decoded_url[len("/media/") :]

            # ":/"를 "://"로 수정
            decoded_url = decoded_url.replace(":/", "://", 1)  # 첫 번째 발생만 변경

            return decoded_url
        return None  # 이미지가 없을 경우


class UserInfoSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "profile_image", "is_expert"]
        read_only_fields = ("id", "email")

    def get_profile_image(self, obj):
        """
        UserInfoSerializer에서도 동일하게 profile_image 처리.
        """
        if obj.profile_image:
            # URL 디코딩 처리
            decoded_url = urllib.parse.unquote(obj.profile_image.url)

            # "/media/" 제거
            if decoded_url.startswith("/media/"):
                decoded_url = decoded_url[len("/media/") :]

            # ":/"를 "://"로 수정
            decoded_url = decoded_url.replace(":/", "://", 1)  # 첫 번째 발생만 변경

            return decoded_url
        return None
