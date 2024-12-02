from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"  # 정적 파일은 공개


class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False  # 동일 파일명이 있을 경우 덮어쓰지 않음
