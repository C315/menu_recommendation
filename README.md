# Slack 점심 메뉴 추천 챗봇

나이, 성별, 음식 취향, 현재 계절을 반영하여 Gemini API로 점심 메뉴 3개를 추천해주는 Slack 챗봇입니다.

## Slack App 설정

1. https://api.slack.com/apps → **Create New App** → From scratch
2. **Socket Mode** 활성화 → App-level token 생성 (`connections:write`) → `SLACK_APP_TOKEN`
3. **OAuth & Permissions** → Bot Token Scopes:
   - `app_mentions:read`, `chat:write`, `im:history`, `im:read`, `commands`
4. **Slash Commands** → 아래 커맨드 3개 생성:
   - `/register` (설명: "나이와 성별 등록")
   - `/likes` (설명: "좋아하는 음식 등록")
   - `/dislikes` (설명: "싫어하는 음식 등록")
5. **Event Subscriptions** 활성화 → Subscribe to bot events:
   - `app_mention`, `message.im`
6. **Install to Workspace** → Bot User OAuth Token → `SLACK_BOT_TOKEN`
7. **App Home** → Messages Tab 활성화, DM 허용 체크

## 실행 방법

```bash
cd D:/menu_recommendation
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

`.env` 파일에 토큰을 입력합니다:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
GEMINI_API_KEY=...
```

Gemini API 키는 https://aistudio.google.com/apikey 에서 발급받을 수 있습니다.

```bash
python app.py
```

## 사용법

| 명령 | 설명 |
|------|------|
| `/register 30 남자` | 나이와 성별 등록 |
| `/likes 된장찌개, 파스타, 초밥` | 좋아하는 음식 등록 |
| `/dislikes 생선, 낙지` | 싫어하는 음식 등록 |
| `@봇 오늘 점심 뭐 먹지?` | 채널에서 메뉴 추천 요청 |
| `@봇 매운 거 추천해줘` | 조건 추가하여 추천 요청 |
| DM으로 메시지 전송 | 1:1 대화로 메뉴 추천 요청 |
