# Skin Analysis AI Web Application

얼굴 사진과 피부 MBTI 설문을 함께 활용해 피부 상태를 분석하고 맞춤형 관리 가이드를 제공하는 웹 애플리케이션입니다.  
Flask 프론트엔드와 FastAPI 백엔드를 분리해 구성했으며, 이미지 분석 로직과 ML 예측 로직을 함께 사용할 수 있습니다.

## 주요 기능

- 얼굴 사진 업로드 기반 피부 분석
- 얼굴 검출을 통한 업로드 이미지 1차 검증
- 주름, 모공, 붉은기, 색소침착, 유분 밸런스 등 복합 지표 분석
- 피부 MBTI 설문 기반 체질 보정
- 종합 점수, 핵심 고민, 추천 루틴, 추천 제품 카테고리 제공
- Flask 기반 반응형 웹 UI

## 기술 구성

- Frontend: Flask, Jinja2
- Backend: FastAPI
- Image Processing: OpenCV
- ML: TensorFlow / Keras

## 실행 환경

- Python 3.8 이상

## 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

### 1. FastAPI 백엔드 실행

```bash
python main.py
```

기본 주소: `http://127.0.0.1:8000`

### 2. Flask 프론트엔드 실행

```bash
python app.py
```

기본 주소: `http://127.0.0.1:5000`

브라우저에서 `http://127.0.0.1:5000`에 접속하면 됩니다.

## 빠른 점검

- Flask 상태 확인: `GET /health`
- FastAPI 상태 확인: `GET /health`
- 통합 점검 스크립트: `python health_check.py`

## 프로젝트 구조

```text
myproject/
├─ app.py                 # Flask 프론트엔드
├─ main.py                # FastAPI 백엔드
├─ skin_analyzer.py       # OpenCV 기반 피부 분석 엔진
├─ skin_model.py          # ML 예측 로직
├─ config.py              # 공통 설정
├─ constants.py           # 상수 정의
├─ logger.py              # 로깅 설정
├─ utils.py               # 유틸리티 함수
├─ templates/
│  ├─ index.html          # 업로드/설문 페이지
│  └─ result.html         # 결과 리포트 페이지
├─ static/
│  ├─ style.css           # 공통 스타일
│  └─ script.js           # 프론트 보조 스크립트
├─ data/                  # 데이터셋 및 라벨
├─ model/                 # 학습된 모델
└─ uploads/               # 업로드 파일 저장 경로
```

## 분석 결과 예시

- 종합 피부 점수
- 예상 나이 / 예상 성별
- 피부 MBTI 코드
- 우선 관리 포인트
- 세부 상태 카드
- 추천 제품 카테고리
- 아침 / 저녁 루틴

## 설정

세부 설정은 `config.py`에서 관리합니다.

- 서버 주소 및 포트
- 업로드 허용 용량
- 모델 경로
- 분석 임계값

## 문서

- `UPGRADE_SUMMARY.md`: 업그레이드 상세 내역
- `UPGRADE_COMPLETE.md`: 업그레이드 요약
- `QUICKSTART.md`: 빠른 시작 가이드

## 문제 해결

- 얼굴이 감지되지 않으면 정면 얼굴 사진으로 다시 시도해 주세요.
- 백엔드 연결 오류가 발생하면 `main.py`가 실행 중인지 확인해 주세요.
- 모델 로딩 문제가 있으면 `train_simple.py` 또는 `train_skin_model.py`로 모델을 다시 생성해 주세요.
- 업로드가 거부되면 파일 형식과 용량 제한을 확인해 주세요.

## 참고

이 프로젝트의 분석 결과는 참고용이며, 실제 피부 질환 진단이나 치료 판단은 전문 의료진 상담이 필요합니다.
