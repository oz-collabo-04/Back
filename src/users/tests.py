from django.test import TestCase

from users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        # 일반 사용자 생성
        self.user = User.objects.create_user(
            email="testuser@example.com", name="Test User", gender="M", phone_number="01012345678"
        )

        # 슈퍼유저 생성
        self.superuser = User.objects.create_superuser(email="admin@example.com", password="adminpassword")

    def test_create_user(self):
        # 일반 사용자 생성 테스트
        self.assertEqual(self.user.email, "testuser@example.com")  # 이메일이 올바르게 설정되었는지 확인
        self.assertEqual(self.user.name, "Test User")  # 이름이 올바르게 설정되었는지 확인
        self.assertEqual(self.user.gender, "M")  # 성별이 올바르게 설정되었는지 확인
        self.assertEqual(self.user.phone_number, "01012345678")  # 전화번호가 올바르게 설정되었는지 확인
        self.assertTrue(self.user.is_active)  # 사용자가 활성 상태인지 확인
        self.assertFalse(self.user.is_staff)  # 일반 사용자는 관리자가 아님을 확인
        self.assertFalse(self.user.is_superuser)  # 일반 사용자는 슈퍼유저가 아님을 확인
        self.assertTrue(self.user.has_usable_password() is False)  # 비밀번호가 설정되지 않았음을 확인 (사용 불가 상태)

    def test_create_superuser(self):
        # 슈퍼유저 생성 테스트
        self.assertEqual(self.superuser.email, "admin@example.com")  # 이메일이 올바르게 설정되었는지 확인
        self.assertTrue(self.superuser.is_active)  # 슈퍼유저가 활성 상태인지 확인
        self.assertTrue(self.superuser.is_staff)  # 슈퍼유저는 관리자임을 확인
        self.assertTrue(self.superuser.is_superuser)  # 슈퍼유저임을 확인

    def test_user_string_representation(self):
        # 사용자 문자열 표현 테스트 (__str__ 메서드)
        self.assertEqual(str(self.user), self.user.email)  # 사용자 객체의 문자열 표현이 이메일과 일치하는지 확인

    def test_unique_email(self):
        # 이메일 중복 테스트
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="testuser@example.com", name="Duplicate User", gender="F", phone_number="01098765432"
            )  # 중복된 이메일을 가진 사용자를 생성하면 예외가 발생하는지 확인

    def test_prefer_service_field(self):
        # 선호 서비스 필드 설정 테스트
        self.user.prefer_service = ["mc", "snap"]  # 선호 서비스 설정
        self.user.save()
        self.assertEqual(self.user.prefer_service, ["mc", "snap"])  # 설정된 값이 올바른지 확인

    def test_prefer_location_field(self):
        # 선호 지역 필드 설정 테스트
        self.user.prefer_location = ["seoul", "gyeonggi_suwon"]  # 선호 지역 설정
        self.user.save()
        self.assertEqual(self.user.prefer_location, ["seoul", "gyeonggi_suwon"])  # 설정된 값이 올바른지 확인
