# Render Web Service 배포 방법

Blueprint가 아니라 Web Service로 배포해도 됩니다. 이 저장소는 Web Service에서 바로 실행되도록 준비되어 있습니다.

## 이미 준비된 것

- 배포용 실행 파일: `deploy_app.py`
- 운영 서버 실행 패키지: `gunicorn`
- Python 버전 고정: `.python-version`
- AI 모델 파일: `model/skin_model_best.pth`
- 실행 명령 예시: `Procfile`

## Render 설정값

Render에서 `New +` > `Web Service`를 선택한 뒤 아래 값으로 설정합니다.

```text
Repository: fhfcpwlwl/SW-test
Branch: main
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn deploy_app:app --bind 0.0.0.0:$PORT --timeout 180
Instance Type: Free
```

환경변수는 아래 값만 추가하면 됩니다.

```text
PYTHON_VERSION=3.11.9
PYTORCH_MODEL_PATH=model/skin_model_best.pth
PYTORCH_MODEL_LABELS=acne,normal
FLASK_DEBUG=False
LOG_LEVEL=INFO
```

`.python-version`도 추가해두었지만, Render 설정 화면에도 `PYTHON_VERSION=3.11.9`를 넣어두면 가장 확실합니다.

## 배포 후 확인

배포 완료 후 Render가 만들어준 주소 뒤에 `/health`를 붙여 접속합니다.

```text
https://서비스이름.onrender.com/health
```

아래처럼 나오면 정상입니다.

```json
{
  "status": "ok",
  "service": "flask-deploy",
  "model_loaded": true
}
```

그 다음 `/` 주소로 접속해서 시연하면 됩니다.

## 무료 플랜 주의사항

무료 Web Service는 15분 동안 요청이 없으면 잠시 잠들 수 있습니다. 링크는 계속 유지되지만, 첫 접속 때 다시 켜지느라 약 1분 정도 걸릴 수 있습니다.
