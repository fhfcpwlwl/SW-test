# Render 배포 방법

ngrok는 내 컴퓨터가 켜져 있고 서버가 실행 중일 때만 접속됩니다.  
항상 공유 가능한 시연 링크가 필요하면 Render 같은 클라우드 서버에 배포해야 합니다.

## 1. GitHub에 올릴 파일

아래 파일들이 커밋에 포함되어야 합니다.

```bash
git add deploy_app.py render.yaml Procfile requirements.txt DEPLOY_RENDER.md
git add model/skin_model_best.pth
git commit -m "Add Render deployment config"
git push
```

`model/skin_model.h5`는 300MB가 넘고 현재 배포 앱에서 쓰지 않으므로 올리지 않아도 됩니다.

## 2. Render에서 서비스 만들기

1. https://render.com 에 로그인합니다.
2. New > Blueprint를 선택합니다.
3. 이 프로젝트가 올라간 GitHub 저장소를 연결합니다.
4. `render.yaml` 설정을 확인하고 Apply를 누릅니다.
5. 배포가 끝나면 `https://...onrender.com` 형태의 링크가 생성됩니다.

## 3. 배포 후 확인

배포된 주소 뒤에 `/health`를 붙여서 접속합니다.

```text
https://배포주소.onrender.com/health
```

아래처럼 나오면 모델까지 정상 로드된 상태입니다.

```json
{
  "status": "ok",
  "service": "flask-deploy",
  "model_loaded": true
}
```

## 참고

Render 무료 플랜은 15분 동안 요청이 없으면 서버가 잠시 잠들 수 있습니다. 그래도 누군가 링크에 접속하면 자동으로 다시 켜지며, 첫 접속만 약 1분 정도 느릴 수 있습니다. 발표나 시연에서 첫 접속 지연도 없어야 하면 Render 유료 인스턴스를 사용하세요.
