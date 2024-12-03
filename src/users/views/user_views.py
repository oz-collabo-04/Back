from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.logging_config import logger
from users.serializers.user_serializers import UserSerializer


# 유저 상세내역, 정보수정, 삭제 뷰
class UserEditView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """현재 로그인된 사용자 반환"""
        return self.request.user

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 사용자 - 상세 조회",
        responses={200: UserSerializer()},
    )
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        logger.info(f"User {user.id} details requested.")
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 사용자 - 전체 수정",
        responses={200: UserSerializer()},
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {instance.id} updated all details.")
        return Response(serializer.data)

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 사용자 - 부분 수정",
        responses={200: UserSerializer},
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # 부분 수정임을 명시
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {instance.id} updated partial details.")
        return Response(serializer.data)

    @extend_schema(
        tags=["X"],
        summary="소프트 딜리트 사용으로 - 사용하지 않는 api",
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"User {instance.id} deleted all details.")
        instance.delete()
        logger.info(f"User {instance.id} deleted all details.")
        return Response(status=status.HTTP_200_OK)


# 고객 회원 탈퇴 뷰 / is_active 상태 False로 변경
class UserDeactivateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """현재 로그인된 사용자 반환"""
        return self.request.user

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 user의 is_active 상태 변경",
        description="현재 로그인된 사용자의 `is_active` 상태를 False로 설정하여 비활성화(회원 탈퇴)합니다.",
        responses={
            200: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "회원탈퇴에 성공했습니다."}},
            },
            400: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "잘못된 요청입니다."}},
            },
            401: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "인증이 필요합니다."}},
            },
        },
    )
    def patch(self, request, *args, **kwargs):
        try:
            # 실제 삭제 대신 is_active 필드를 False로 설정
            instance = self.get_object()

            if not instance.is_active:
                logger.warning(f"User {instance.id} attempted deactivation but is already inactive.")
                return Response(
                    {"detail": "이미 비활성화된 사용자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.is_active = False
            instance.save()
            logger.info(f"User {instance.id} successfully deactivated.")
            return Response({"detail": "회원탈퇴에 성공했습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return Response(
                {"detail": "회원탈퇴 처리 중 오류가 발생했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
