import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from estimations.models import EstimationsRequest, RequestManager
from expert.models import Expert

# 로거 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로깅 레벨 설정

# StreamHandler 생성
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)  # 핸들러의 로깅 레벨 설정

# 로그 출력 형식 지정
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)  # 핸들러에 포매터 설정

# 핸들러를 로거에 추가
logger.addHandler(stream_handler)

@receiver(post_save, sender=EstimationsRequest)
def estimations_request_signals(sender, instance, created, **kwargs):
    logger.info('전문가를 위한 요청 객체 생성')
    if created:
        experts = Expert.objects.filter(
            available_location__contains=instance.location,
            user__gender=instance.prefer_gender,
            service__in=instance.service_list,
        )
        # RequestManager 객체를 생성할 리스트
        request_managers = [
            RequestManager(
                estimation_request=instance,
                expert=expert
            )
            for expert in experts
        ]
        # bulk_create로 한번의 쿼리로 모든 객체를 데이터베이스에 저장.
        RequestManager.objects.bulk_create(request_managers)