from decimal import Decimal

SERVICE_CHOICES = [
    ("mc", "결혼식 사회자"),
    ("snap", "스냅 촬영"),
    ("singer", "축가 가수"),
    ("video", "영상 촬영"),
]

AREA_CHOICES = [
    # 특별시 및 광역시
    ("seoul", "서울특별시"),
    ("busan", "부산광역시"),
    ("incheon", "인천광역시"),
    ("daegu", "대구광역시"),
    ("daejeon", "대전광역시"),
    ("gwangju", "광주광역시"),
    ("ulsan", "울산광역시"),
    ("sejong", "세종특별시"),
    ("jeju", "제주특별자치도"),
    # 경기도
    ("gyeonggi_suwon", "경기도 수원시"),
    ("gyeonggi_seongnam", "경기도 성남시"),
    ("gyeonggi_yongin", "경기도 용인시"),
    ("gyeonggi_bucheon", "경기도 부천시"),
    ("gyeonggi_anyang", "경기도 안양시"),
    ("gyeonggi_ansan", "경기도 안산시"),
    ("gyeonggi_goyang", "경기도 고양시"),
    ("gyeonggi_pyeongtaek", "경기도 평택시"),
    ("gyeonggi_paju", "경기도 파주시"),
    ("gyeonggi_gimpo", "경기도 김포시"),
    ("gyeonggi_icheon", "경기도 이천시"),
    ("gyeonggi_pocheon", "경기도 포천시"),
    ("gyeonggi_namyangju", "경기도 남양주시"),
    ("gyeonggi_hwaseong", "경기도 화성시"),
    # 강원도
    ("gangwon_chuncheon", "강원도 춘천시"),
    ("gangwon_wonju", "강원도 원주시"),
    ("gangwon_gangneung", "강원도 강릉시"),
    ("gangwon_donghae", "강원도 동해시"),
    ("gangwon_sokcho", "강원도 속초시"),
    ("gangwon_samcheok", "강원도 삼척시"),
    # 충청북도
    ("chungbuk_cheongju", "충청북도 청주시"),
    ("chungbuk_chungju", "충청북도 충주시"),
    ("chungbuk_jecheon", "충청북도 제천시"),
    ("chungbuk_okkcheon", "충청북도 옥천군"),
    ("chungbuk_danyang", "충청북도 단양군"),
    # 충청남도
    ("chungnam_cheonan", "충청남도 천안시"),
    ("chungnam_asan", "충청남도 아산시"),
    ("chungnam_seosan", "충청남도 서산시"),
    ("chungnam_boryeong", "충청남도 보령시"),
    ("chungnam_nonsan", "충청남도 논산시"),
    # 전라북도
    ("jeonbuk_jeonju", "전라북도 전주시"),
    ("jeonbuk_gunsan", "전라북도 군산시"),
    ("jeonbuk_iksan", "전라북도 익산시"),
    ("jeonbuk_namwon", "전라북도 남원시"),
    ("jeonbuk_jeongeup", "전라북도 정읍시"),
    # 전라남도
    ("jeonnam_mokpo", "전라남도 목포시"),
    ("jeonnam_yeosu", "전라남도 여수시"),
    ("jeonnam_suncheon", "전라남도 순천시"),
    ("jeonnam_naju", "전라남도 나주시"),
    ("jeonnam_gwangyang", "전라남도 광양시"),
    # 경상북도
    ("gyeongbuk_pohang", "경상북도 포항시"),
    ("gyeongbuk_gyeongju", "경상북도 경주시"),
    ("gyeongbuk_gimcheon", "경상북도 김천시"),
    ("gyeongbuk_andong", "경상북도 안동시"),
    ("gyeongbuk_gumi", "경상북도 구미시"),
    ("gyeongbuk_mungyeong", "경상북도 문경시"),
    # 경상남도
    ("gyeongnam_changwon", "경상남도 창원시"),
    ("gyeongnam_jinju", "경상남도 진주시"),
    ("gyeongnam_tongyeong", "경상남도 통영시"),
    ("gyeongnam_sacheon", "경상남도 사천시"),
    ("gyeongnam_gimhae", "경상남도 김해시"),
    ("gyeongnam_miryang", "경상남도 밀양시"),
]

RESERVATION_STATUS_CHOICES = [
    ("confirmed", "예약 확정"),
    ("canceled", "예약 취소"),
    ("completed", "서비스 완료"),
]

RATING_CHOICES = [
    (Decimal("0.5"), "zero_point_five"),
    (Decimal("1.0"), "one"),
    (Decimal("1.5"), "one_point_five"),
    (Decimal("2.0"), "two"),
    (Decimal("2.5"), "two_point_five"),
    (Decimal("3.0"), "three"),
    (Decimal("3.5"), "three_point_five"),
    (Decimal("4.0"), "four"),
    (Decimal("4.5"), "four_point_five"),
    (Decimal("5.0"), "five"),
]

NOTIFICATION_TYPE_CHOICES = [
    ("message", "채팅 메시지 알림"),  # 채팅방에 읽지않은 메시지가 도착했을 때
    ("reserved", "예약 확정 알림"),  # 채팅방에서 상호 합의로 예약을 확정 지었을 때 알림
    ("review", "리뷰 등록 알림"),  # 서비스를 이용한 유저가 예약에 대한 리뷰를 작성 했을 때 알림
    ("estimation", "견적 알림"),  # 유저가 신청한 견적 요청에 따라 전문가가 견적을 발송했을 때 알림
    ("estimation_request", "견적 요청 알림"),  # 유저가 견적을 요청했을 때 알림
    ("usage", "이용 완료 알림"),  # 유저가 서비스를 이용하고 난후 알림
    ("schedule", "일정 알림"),  # 전문가에게 예약된 일정을 알려줌
]

PREFER_GENDER_CHOICES = [("M", "남성"), ("F", "여성"), ("ANY", "상관없음")]

GENDER_CHOICES = [
    ("M", "남성"),
    ("F", "여성"),
]

REQUEST_STATUS_CHOICES = [("pending", "견적 요청중"), ("completed", "견적 받기 완료"), ("canceled", "견적 요청 취소")]

VALID_LOCATION = [item[0] for item in AREA_CHOICES]
