from dotenv import load_dotenv

load_dotenv()

from app import app, SocketModeHandler
import os


def main():
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Bolt app is running!")
    handler.start()


if __name__ == "__main__":
    main()
