from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.seriailzers import UserSerializer


# 유저 상세내역, 정보수정, 삭제 뷰
class UserEditView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 사용자 - 상세 조회",
        responses={200: UserSerializer()},
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        return self.request.user

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
        return Response(serializer.data)


# 고객 회원 탈퇴 뷰 / is_active 상태 False로 변경
class UserDeactivateView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그인 된 user의 is_active 상태 변경",
        responses={
            200: {"type": "object", "properties": {"detail": {"type": "string", "example": "회원탈퇴에 성공했습니다."}}}
        },
    )
    def patch(self, request, *args, **kwargs):
        # 실제 삭제 대신 is_active 필드를 False로 설정
        instance = self.get_object()
        instance.is_active = False
        instance.save()  # 인스턴스를 저장하여 변경사항 반영
        return Response({"detail": "회원탈퇴에 성공했습니다."}, status=status.HTTP_204_NO_CONTENT)
