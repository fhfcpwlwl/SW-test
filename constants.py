"""
Constants and magic numbers used throughout the application
"""

# API Response Status Codes
STATUS_SUCCESS = 200
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404
STATUS_INTERNAL_ERROR = 500

# Skin Analysis Range Constants
MIN_SCORE = 0
MAX_SCORE = 100
MIN_AGE = 18
MAX_AGE = 60

# Color Space Constants
BGR_TO_RGB_WEIGHTS = [0.2989, 0.5870, 0.1140]

# HSV Color Range for Brown Pigmentation
PIGMENTATION_HUE_MIN = 0.04
PIGMENTATION_HUE_MAX = 0.15
PIGMENTATION_SATURATION_MIN = 0.25

# Skin Pixel Detection Thresholds
SKIN_R_MIN = 95
SKIN_G_MIN = 40
SKIN_B_MIN = 20
SKIN_RG_DIFF_MIN = 15
SKIN_RB_DIFF_MIN = 15

# Image Processing Constants
DEFAULT_IMAGE_SIZE = (320, 320)
MODEL_IMAGE_SIZE = (224, 224)

# Confidence Levels
CONFIDENCE_HIGH = 0.8
CONFIDENCE_MEDIUM = 0.6
CONFIDENCE_LOW = 0.4

# Error Messages
ERROR_NO_FILE = "파일이 없습니다."
ERROR_NO_FACE = "얼굴이 감지되지 않았습니다. 정면 얼굴 사진을 업로드해주세요."
ERROR_INVALID_FORMAT = "지원하지 않는 파일 형식입니다."
ERROR_FILE_TOO_LARGE = "파일 크기가 너무 큽니다."
ERROR_PROCESSING = "이미지를 처리할 수 없습니다."
ERROR_SERVER = "서버 오류가 발생했습니다."
ERROR_TIMEOUT = "서버 응답 시간 초과"
ERROR_CONNECTION = "백엔드 서버에 연결할 수 없습니다."

# Success Messages
SUCCESS_ANALYSIS = "분석이 완료되었습니다."
SUCCESS_MODEL_LOADED = "모델이 성공적으로 로드되었습니다."
SUCCESS_FILE_UPLOADED = "파일이 성공적으로 업로드되었습니다."

# Skin Condition Thresholds
SEVERE_WRINKLES = 70
SEVERE_ACNE = 70
POOR_HEALTH = 30
EXCELLENT_HEALTH = 80

# ML Model Properties
TRANSFER_LEARNING = True
BASE_MODEL = "MobileNetV2"
DROPOUT_RATE = 0.3
LEARNING_RATE = 1e-4
OPTIMIZATION = "adam"
LOSS_FUNCTION = "mse"

# Analysis Output Structure
ANALYSIS_KEYS = [
    "overall_acne",
    "overall_stain", 
    "overall_health",
    "wrinkles",
    "pores",
    "redness",
    "acne_inflamed",
    "acne_noninflamed",
    "skin_tone",
    "sagging",
    "pigmentation",
    "oil_balance",
    "age_estimate",
    "gender_guess",
]
