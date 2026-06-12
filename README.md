# SW Skin Test

사진 업로드와 간단한 피부 설문을 바탕으로 피부 상태를 분석하고, 관리 우선순위와 추천 루틴을 보여주는 AI 피부 분석 웹 애플리케이션입니다.

## 주요 기능

- 얼굴 사진 업로드 기반 PyTorch 피부 상태 분류
- 여드름성 피부와 정상 피부 경향 판정
- 설문 기반 피부 성향 보정
- 관리 우선순위, 상세 분석 요약, 추천 루틴, 추천 제품 표시
- Flask 프론트엔드와 FastAPI 백엔드 분리 구조

## 기술 스택

- Frontend: Flask, Jinja2, HTML, CSS, JavaScript
- Backend: FastAPI, Uvicorn
- AI / Image Processing: PyTorch, Torchvision, OpenCV, Pillow

## 실행 준비

Python 3.9 이상을 권장합니다.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 모델 파일

기본 모델 위치는 아래 경로입니다.

```text
model/skin_model_best.pth
```

다른 위치의 모델을 쓰려면 `.env` 파일을 만들고 다음처럼 설정합니다.

```env
PYTORCH_MODEL_PATH=C:\path\to\skin_model_best.pth
PYTORCH_MODEL_LABELS=acne,normal
```

## 실행 방법

터미널 2개를 열어 백엔드와 프론트엔드를 각각 실행합니다.

### 1. 백엔드 실행

```bash
python main.py
```

백엔드 주소: `http://127.0.0.1:8000`

### 2. 프론트엔드 실행

```bash
python app.py
```

웹 화면 주소: `http://127.0.0.1:5000`

## 상태 확인

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:5000/health
```

백엔드 응답에서 `model_loaded`가 `true`이면 모델이 정상 로드된 상태입니다.

## 프로젝트 구조

```text
SW-skin-test/
├── app.py                  # Flask 프론트엔드
├── main.py                 # FastAPI 백엔드
├── config.py               # 환경 설정
├── torch_skin_model.py     # PyTorch 모델 로딩 및 예측
├── pytorch_report.py       # 결과 리포트 생성
├── skin_analyzer.py        # 이미지 분석 보조 로직
├── templates/              # 화면 템플릿
├── static/                 # CSS, JavaScript
├── data/                   # 예시 데이터
├── model/                  # 모델 파일 위치
└── requirements.txt
```

## 주의

이 결과는 사진 분석과 설문 응답을 바탕으로 한 스킨케어 참고용 안내입니다. 질환 진단이나 치료 판단을 대체하지 않습니다.
