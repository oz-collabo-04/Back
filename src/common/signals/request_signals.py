from django.db.models.signals import post_save
from django.dispatch import receiver

from estimations.models import EstimationsRequest, RequestManager
from expert.models import Expert
from notifications.models import Notification


@receiver(post_save, sender=EstimationsRequest)
def estimation_request_post_save_handler(sender, instance, created, **kwargs):
    if created:
        request = instance

        # 서비스 리스트를 필터링할 수 있는 형식으로 변환 (예: 콤마로 구분된 문자열을 리스트로 변환)
        service_list = (
            request.service_list.split(",") if isinstance(request.service_list, str) else request.service_list
        )

        # 관련 전문가 필터링
        experts = Expert.objects.filter(
            service__in=service_list,
            # user__gender=request.prefer_gender,
            available_location__contains=request.location,
        )
        RequestManager.objects.bulk_create([RequestManager(request=request, expert=expert) for expert in experts])

        # 전문가들에게 알림 생성
        for expert in experts:
            Notification.objects.create(
                receiver=expert.user,
                title=f"{request.user.name}님이 견적 요청을 보냈습니다. 확인해보세요!",
                message=(
                    f"- 요청 서비스: {request.get_service_list_display()}\n"
                    f"- 선호 하는 성별: {request.get_prefer_gender_display()}\n"
                    f"- 결혼식 정보:\n"
                    f"  - 결혼식 예상 지역: {request.get_location_display()}\n"
                    f"  - 결혼식장: {request.wedding_hall}\n"
                    f"  - 결혼식 예상 날짜: {request.wedding_datetime}\n"
                ),
                notification_type="estimation_request",
                is_read=False,
            )
