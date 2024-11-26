from decimal import Decimal

SERVICE_CHOICES = [
    ("mc", "MC"),
    ("snap", "스냅"),
    ("singer", "가수"),
    ("video", "영상"),
]

AREA_CHOICES = [
    # 특별시 및 광역시
    ("seoul", "서울"),
    ("busan", "부산"),
    ("incheon", "인천"),
    ("daegu", "대구"),
    ("daejeon", "대전"),
    ("gwangju", "광주"),
    ("ulsan", "울산"),
    ("sejong", "세종"),
    ("jeju", "제주"),
    # 경기도
    ("gyeonggi_suwon", "경기-수원"),
    ("gyeonggi_seongnam", "경기-성남"),
    ("gyeonggi_yongin", "경기-용인"),
    ("gyeonggi_bucheon", "경기-부천"),
    ("gyeonggi_anyang", "경기-안양"),
    ("gyeonggi_ansan", "경기-안산"),
    ("gyeonggi_goyang", "경기-고양"),
    ("gyeonggi_pyeongtaek", "경기-평택"),
    ("gyeonggi_paju", "경기-파주"),
    ("gyeonggi_gimpo", "경기-김포"),
    ("gyeonggi_icheon", "경기-이천"),
    ("gyeonggi_pocheon", "경기-포천"),
    ("gyeonggi_namyangju", "경기-남양주"),
    ("gyeonggi_hwaseong", "경기-화성"),
    # 강원도
    ("gangwon_chuncheon", "강원-춘천"),
    ("gangwon_wonju", "강원-원주"),
    ("gangwon_gangneung", "강원-강릉"),
    ("gangwon_donghae", "강원-동해"),
    ("gangwon_sokcho", "강원-속초"),
    ("gangwon_samcheok", "강원-삼척"),
    # 충청북도
    ("chungbuk_cheongju", "충북-청주"),
    ("chungbuk_chungju", "충북-충주"),
    ("chungbuk_jecheon", "충북-제천"),
    ("chungbuk_okkcheon", "충북-옥천"),
    ("chungbuk_danyang", "충북-단양"),
    # 충청남도
    ("chungnam_cheonan", "충남-천안"),
    ("chungnam_asan", "충남-아산"),
    ("chungnam_seosan", "충남-서산"),
    ("chungnam_boryeong", "충남-보령"),
    ("chungnam_nonsan", "충남-논산"),
    # 전라북도
    ("jeonbuk_jeonju", "전북-전주"),
    ("jeonbuk_gunsan", "전북-군산"),
    ("jeonbuk_iksan", "전북-익산"),
    ("jeonbuk_namwon", "전북-남원"),
    ("jeonbuk_jeongeup", "전북-정읍"),
    # 전라남도
    ("jeonnam_mokpo", "전남-목포"),
    ("jeonnam_yeosu", "전남-여수"),
    ("jeonnam_suncheon", "전남-순천"),
    ("jeonnam_naju", "전남-나주"),
    ("jeonnam_gwangyang", "전남-광양"),
    # 경상북도
    ("gyeongbuk_pohang", "경북-포항"),
    ("gyeongbuk_gyeongju", "경북-경주"),
    ("gyeongbuk_gimcheon", "경북-김천"),
    ("gyeongbuk_andong", "경북-안동"),
    ("gyeongbuk_gumi", "경북-구미"),
    ("gyeongbuk_mungyeong", "경북-문경"),
    # 경상남도
    ("gyeongnam_changwon", "경남-창원"),
    ("gyeongnam_jinju", "경남-진주"),
    ("gyeongnam_tongyeong", "경남-통영"),
    ("gyeongnam_sacheon", "경남-사천"),
    ("gyeongnam_gimhae", "경남-김해"),
    ("gyeongnam_miryang", "경남-밀양"),
]

RESERVATION_STATUS_CHOICES = [
    ("pending", "진행중"),
    ("confirmed", "예약 확정"),
    ("cancel", "예약 취소"),
    ("cancelling", "취소중"),
    ("completed", "완료"),
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
    ("message", "메시지 알림"),
    ("contract", "예약 알림"),
    ("estimate", "견적 알림"),
    ("usage", "이용 알림"),
    ("schedule", "일정 알림"),
]

GENDER_CHOICES = [
    ("M", "남성"),
    ("F", "여성"),
]

REQUEST_STATUS_CHOICES = [("pending", "견적 요청중"), ("completed", "견적 받기 완료"), ("canceled", "견적 요청 취소")]
