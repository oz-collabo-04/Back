from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from multiselectfield import MultiSelectField

from common.constants.choices import AREA_CHOICES, GENDER_CHOICES, SERVICE_CHOICES


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        name,
        gender,
        phone_number,
        **kwargs,
    ):
        kwargs.setdefault("is_active", True)
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            gender=gender,
            phone_number=phone_number,
            **kwargs,
        )

        user.set_unusable_password()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_staff", True)

        user = self.model(email=email, **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=30, unique=True)
    name = models.CharField(max_length=25)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=13)
    prefer_service = MultiSelectField(choices=SERVICE_CHOICES, max_length=10, null=True, blank=True)
    prefer_location = MultiSelectField(choices=AREA_CHOICES, max_length=30, max_choices=3, null=True, blank=True)
    profile_image = models.ImageField(max_length=200, null=True, blank=True, upload_to="images/users/profile/")
    is_active = models.BooleanField(default=True)
    is_expert = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    objects = UserManager()
