import logging

from rest_framework.exceptions import APIException

# Logger 설정
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


class CustomAPIException(APIException):
    status_code = 400
    default_detail = "요청 처리 중 오류가 발생했습니다."
    default_code = "error"

    def __init__(self, detail=None, code=None, status_code=None):
        # 로깅 추가
        logger.error(f"Error occurred - Code: {code}, Detail: {detail}")

        # 상태 코드가 제공되면 재설정
        if status_code:
            self.status_code = status_code

        # 상세 메시지 설정
        self.detail = detail if detail else self.default_detail

        # 코드 설정
        self.code = code if code else self.default_code
