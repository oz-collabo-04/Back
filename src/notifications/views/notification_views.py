from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers.notification_serializers import (
    NotificationReadSerializer,
    NotificationSerializer,
)


@extend_schema(tags=["Notification"])
class NotificationListAPIView(generics.ListAPIView):
    """
    해당 유저에 대한 알림 목록 조회 및 읽지 않은 알림의 수를 같이 반환 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(receiver_id=user.id, is_read=False)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"unread_count": queryset.count(), "notifications": serializer.data})


@extend_schema(tags=["Notification"])
class NotificationDetailAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    """
    특정 알림 읽음 처리 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationReadSerializer

    def get_object(self):
        notification_id = self.kwargs.get("notification_id")
        return get_object_or_404(Notification, id=notification_id, receiver_id=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema(tags=["Notification"])
class NotificationReadAllAPIView(APIView):
    """
    전체 알림 읽음 처리 API
    """

    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        notifications = Notification.objects.filter(receiver_id=user.id, is_read=False)
        notifications.update(is_read=True)
        return Response({"detail": "전체 알림이 읽음 처리되었습니다."}, status=status.HTTP_200_OK)
