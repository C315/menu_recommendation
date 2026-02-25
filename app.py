import os
import re

from dotenv import load_dotenv

load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import gemini_client
import user_store

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/register")
def handle_register(ack, command, respond):
    ack()
    text = command.get("text", "").strip()
    parts = text.split()

    if len(parts) != 2:
        respond("사용법: `/register [나이] [성별]`\n예시: `/register 30 남자`")
        return

    try:
        age = int(parts[0])
    except ValueError:
        respond("나이는 숫자로 입력해주세요.\n예시: `/register 30 남자`")
        return

    gender = parts[1]
    if gender not in ("남자", "여자"):
        respond("성별은 `남자` 또는 `여자`로 입력해주세요.\n예시: `/register 30 남자`")
        return

    user_id = command["user_id"]
    user_store.save_user(user_id, age, gender)
    respond(f"프로필이 등록되었습니다! ({age}세, {gender})")


@app.command("/likes")
def handle_likes(ack, command, respond):
    ack()
    text = command.get("text", "").strip()
    if not text:
        respond("사용법: `/likes 음식1, 음식2, ...`\n예시: `/likes 된장찌개, 파스타, 초밥`")
        return

    foods = [f.strip() for f in text.split(",") if f.strip()]
    user_store.save_preferences(command["user_id"], likes=foods)
    respond(f"좋아하는 음식이 등록되었습니다! ({', '.join(foods)})")


@app.command("/dislikes")
def handle_dislikes(ack, command, respond):
    ack()
    text = command.get("text", "").strip()
    if not text:
        respond("사용법: `/dislikes 음식1, 음식2, ...`\n예시: `/dislikes 생선, 낙지`")
        return

    foods = [f.strip() for f in text.split(",") if f.strip()]
    user_store.save_preferences(command["user_id"], dislikes=foods)
    respond(f"싫어하는 음식이 등록되었습니다! ({', '.join(foods)})")


def _handle_recommendation(user_id: str, message: str, say):
    user = user_store.get_user(user_id)
    if not user:
        say("먼저 `/register 나이 성별`로 프로필을 등록해주세요!\n예시: `/register 30 남자`")
        return

    if not message.strip():
        message = "점심 메뉴 추천해줘"

    try:
        response = gemini_client.get_recommendations(
            message, user["age"], user["gender"],
            likes=user.get("likes"), dislikes=user.get("dislikes"),
        )
        say(response)
    except Exception as e:
        print(f"[ERROR] Gemini API 호출 실패: {e}")
        say(f"추천 생성 중 오류가 발생했습니다: {e}")


@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = event.get("text", "")
    text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    _handle_recommendation(user_id, text, say)


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype"):
        return

    user_id = event["user"]
    text = event.get("text", "")
    _handle_recommendation(user_id, text, say)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Bolt app is running!")
    handler.start()
