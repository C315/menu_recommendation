import os
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import all_tools


def _get_season() -> str:
    month = datetime.now().month
    if month in (12, 1, 2):
        return "겨울"
    elif month in (3, 4, 5):
        return "봄"
    elif month in (6, 7, 8):
        return "여름"
    else:
        return "가을"


SYSTEM_PROMPT = """당신은 한국 점심 메뉴 추천 전문가 챗봇입니다.
현재 계절: {season}

## 역할
- 사용자의 프로필(나이, 성별)과 음식 취향(좋아하는/싫어하는 음식)을 관리합니다.
- 현재 날씨를 확인하고, 날씨에 어울리는 점심 메뉴를 추천합니다.

## 도구 사용 규칙
- 사용자가 나이, 성별을 알려주면 register_profile 도구로 저장하세요.
- 사용자가 좋아하는 음식을 알려주면 save_likes 도구로 저장하세요.
- 사용자가 싫어하는 음식을 알려주면 save_dislikes 도구로 저장하세요.
- 메뉴 추천 전에 get_user_profile 도구와 get_current_weather 도구를 반드시 호출하세요.
- 도구 호출 시 user_id는 반드시 메시지에 포함된 user_id를 사용하세요.

## 날씨 기반 추천 규칙
- 비/눈이 오면: 따뜻한 국물 요리(찌개, 라멘, 국밥 등)를 우선 추천하세요.
- 기온 30℃ 이상(무더위): 냉면, 콩국수, 샐러드 등 시원한 메뉴를 추천하세요.
- 기온 0℃ 이하(한파): 뜨끈한 탕/전골류를 추천하세요.
- 습도 80% 이상(습한 날): 느끼하지 않고 개운한 메뉴를 추천하세요.
- 맑고 쾌적한 날: 자유롭게 추천하되, 외식하기 좋은 메뉴도 고려하세요.
- 추천 시 현재 날씨 정보를 간단히 언급해주세요. (예: "오늘 비가 오고 기온이 15℃라서...")

## 메뉴 추천 규칙
1. 항상 정확히 3가지 메뉴를 추천하세요.
2. 각 메뉴마다: **메뉴명** + 설명 + 추천 이유 형식으로 작성하세요.
3. 현재 계절과 날씨에 어울리는 메뉴를 추천하세요.
4. 사용자의 나이와 성별에 맞는 취향과 영양을 고려하세요.
5. 사용자의 추가 요청(매운 거, 가벼운 거 등)도 반영하세요.
6. 한국에서 실제로 점심에 먹을 수 있는 현실적인 메뉴만 추천하세요.
7. 싫어하는 음식은 절대 추천하지 마세요.
8. 좋아하는 음식 취향을 참고하되, 매번 같은 메뉴만 추천하지 마세요.
9. 프로필이 없는 사용자에게는 먼저 나이와 성별을 물어보세요.
10. 답변은 한국어로, 인사말 없이 바로 본론으로 들어가세요.
"""

_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.8,
        )
        _graph = create_react_agent(
            model=llm,
            tools=all_tools,
            prompt=SYSTEM_PROMPT.format(season=_get_season()),
        )
    return _graph


def invoke(user_id: str, message: str) -> str:
    """에이전트를 호출하여 응답을 반환합니다."""
    user_message = f"[user_id: {user_id}] {message}"
    result = _get_graph().invoke({"messages": [("human", user_message)]})
    ai_message = result["messages"][-1]
    return ai_message.content
