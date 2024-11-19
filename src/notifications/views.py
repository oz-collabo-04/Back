from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@extend_schema(tags=["Notification"])
class NotificationListAPIView(generics.ListAPIView):
    """
    해당 유저에 대한 알림 목록 조회 및 읽지 않은 알림의 수를 같이 반환
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(receiver_id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.filter(is_read=False).count()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "unread_count": unread_count,
            "notifications": serializer.data
        })


@extend_schema(tags=["Notification"])
class NotificationDetailAPIView(generics.UpdateAPIView):
    """
    특정 알림 읽음 처리
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_object(self):
        notification_id = self.kwargs.get('notification_id')
        return get_object_or_404(Notification, id=notification_id, receiver_id=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{self.request.user.id}',
            {
                'type': 'send_notification',
                'message': f'알림 {notification.id}이(가) 읽음 처리되었습니다.'
            }
        )
        return Response(serializer.data)


@extend_schema(tags=["Notification"])
class NotificationReadAllAPIView(generics.UpdateAPIView):
    """
    전체 알림 읽음 처리
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        notifications = Notification.objects.filter(receiver_id=user.id, is_read=False)
        notifications.update(is_read=True)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{user.id}',
            {
                'type': 'send_notification',
                'message': '전체 알림이 읽음 처리되었습니다.'
            }
        )
        return Response({"detail": "전체 알림이 읽음 처리되었습니다."}, status=status.HTTP_200_OK)



