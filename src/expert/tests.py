import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from expert.models import Career, Expert
from users.models import User


class ExpertCreationTestCase(APITestCase):
    def setUp(self):
        """
        테스트에 필요한 기본 데이터 설정
        """
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            gender="M",
            phone_number="010-1234-5678",
        )
        self.user.set_password("qwer1234")
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def generate_test_image(self):
        """
        가상 이미지 파일을 생성하여 SimpleUploadedFile로 반환합니다.
        """
        image = Image.new("RGB", (100, 100), color="blue")
        byte_arr = io.BytesIO()
        image.save(byte_arr, format="JPEG")
        byte_arr.seek(0)
        return SimpleUploadedFile("test_image.jpg", byte_arr.read(), content_type="image/jpeg")

    def test_expert_creation_with_careers(self):
        """
        전문가 프로필과 경력 3개를 포함하여 전문가 정보를 생성하고, is_expert가 True로 변경되는지 테스트
        """
        url = reverse("experts:expert_register")
        data = {
            "service": "mc",
            "standard_charge": 500000,
            "appeal": "어필1",
            "available_location": ["seoul", "busan"],
            "careers": [
                {
                    "title": "Wedding MC",
                    "description": "Worked as a wedding MC for 5 years",
                    "start_date": "2015-01-01",
                    "end_date": "2020-01-01",
                },
                {
                    "title": "Event Host",
                    "description": "Hosted corporate events",
                    "start_date": "2020-02-01",
                    "end_date": "2023-01-01",
                },
                {
                    "title": "Public Speaker",
                    "description": "Delivered motivational speeches",
                    "start_date": "2018-01-01",
                    "end_date": "2021-01-01",
                },
            ],
        }
        data["expert_image"] = self.generate_test_image()

        # 파일 데이터와 JSON 데이터를 혼합하여 전송
        response = self.client.post(url, data, format="multipart")

        # 디버깅용 출력
        print("Response status code:", response.status_code)
        print("Response data:", response.data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_expert)
        self.assertEqual(Career.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expert.objects.count(), 1)
