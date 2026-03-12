import os
import re

from dotenv import load_dotenv

load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import agent

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = re.sub(r"<@[A-Z0-9]+>", "", event.get("text", "")).strip()
    if not text:
        text = "점심 메뉴 추천해줘"
    response = agent.invoke(user_id, text)
    say(response)


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype"):
        return
    user_id = event["user"]
    text = event.get("text", "")
    if not text:
        text = "점심 메뉴 추천해줘"
    response = agent.invoke(user_id, text)
    say(response)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Bolt app is running!")
    handler.start()
