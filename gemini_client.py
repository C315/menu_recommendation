import os
from datetime import datetime

from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


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


def get_recommendations(
    user_message: str,
    age: int = None,
    gender: str = None,
    likes: list[str] = None,
    dislikes: list[str] = None,
) -> str:
    season = _get_season()

    if age and gender:
        user_info = f"사용자 정보: {age}세 {gender}"
    else:
        user_info = "사용자 정보: 없음"

    pref_lines = ""
    if likes:
        pref_lines += f"\n좋아하는 음식: {', '.join(likes)}"
    if dislikes:
        pref_lines += f"\n싫어하는 음식: {', '.join(dislikes)}"

    system_prompt = f"""당신은 한국 점심 메뉴 추천 전문가입니다.

{user_info}{pref_lines}
현재 계절: {season}

규칙:
1. 항상 정확히 3가지 메뉴를 추천하세요.
2. 각 메뉴마다: *메뉴명* + 설명 + 추천 이유 형식
3. 현재 계절에 어울리는 메뉴를 추천하세요 (겨울엔 따뜻한 음식, 여름엔 시원한 음식 등).
4. 사용자의 나이와 성별에 맞는 취향과 영양을 고려하세요.
5. 사용자의 추가 요청(매운 거, 가벼운 거 등)도 반영하세요.
6. 한국에서 실제로 점심에 먹을 수 있는 현실적인 메뉴만 추천하세요.
7. 싫어하는 음식은 절대 추천하지 마세요.
8. 좋아하는 음식 취향을 참고하되, 매번 같은 메뉴만 추천하지 마세요.
9. 답변은 한국어로, 인사말 없이 바로 추천하세요."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.8,
        ),
    )
    return response.text
