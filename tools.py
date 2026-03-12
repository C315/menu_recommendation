import os
from datetime import datetime, timedelta

import requests
from langchain_core.tools import tool

import user_store

KMA_API_KEY = os.environ.get("KMA_API_KEY", "")
# 성수동 기본 좌표 (nx=61, ny=127)
DEFAULT_NX = 61
DEFAULT_NY = 127


@tool
def register_profile(user_id: str, age: int, gender: str) -> str:
    """사용자의 나이와 성별을 등록합니다. 성별은 '남자' 또는 '여자'로 입력합니다."""
    if gender not in ("남자", "여자"):
        return "성별은 '남자' 또는 '여자'로 입력해주세요."
    user_store.save_user(user_id, age, gender)
    return f"프로필이 등록되었습니다! ({age}세, {gender})"


@tool
def save_likes(user_id: str, foods: list[str]) -> str:
    """사용자가 좋아하는 음식 목록을 저장합니다."""
    user_store.save_preferences(user_id, likes=foods)
    return f"좋아하는 음식이 등록되었습니다! ({', '.join(foods)})"


@tool
def save_dislikes(user_id: str, foods: list[str]) -> str:
    """사용자가 싫어하는 음식 목록을 저장합니다."""
    user_store.save_preferences(user_id, dislikes=foods)
    return f"싫어하는 음식이 등록되었습니다! ({', '.join(foods)})"


@tool
def get_user_profile(user_id: str) -> str:
    """사용자의 프로필(나이, 성별, 좋아하는/싫어하는 음식)을 조회합니다."""
    user = user_store.get_user(user_id)
    if not user:
        return "등록된 프로필이 없습니다. 먼저 나이와 성별을 알려주세요."
    parts = [f"나이: {user.get('age')}세, 성별: {user.get('gender')}"]
    if user.get("likes"):
        parts.append(f"좋아하는 음식: {', '.join(user['likes'])}")
    if user.get("dislikes"):
        parts.append(f"싫어하는 음식: {', '.join(user['dislikes'])}")
    return " | ".join(parts)


@tool
def get_current_weather(nx: int = DEFAULT_NX, ny: int = DEFAULT_NY) -> str:
    """현재 날씨 실황을 조회합니다. nx, ny는 기상청 격자 좌표입니다. 기본값은 서울 성수동입니다.

    반환값에 포함되는 항목:
    - T1H: 기온(℃)
    - RN1: 1시간 강수량(mm)
    - REH: 습도(%)
    - PTY: 강수형태(0:없음, 1:비, 2:비/눈, 3:눈, 5:빗방울, 6:빗방울눈날림, 7:눈날림)
    - WSD: 풍속(m/s)
    """
    now = datetime.now()
    # 초단기실황은 매시 정각 기준, 약 40분 후 제공 → 안전하게 1시간 전 사용
    base = now - timedelta(hours=1)
    base_date = base.strftime("%Y%m%d")
    base_time = base.strftime("%H00")

    url = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
        "authKey": KMA_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        items = data["response"]["body"]["items"]["item"]
    except Exception as e:
        return f"날씨 조회 실패: {e}"

    category_names = {
        "T1H": "기온(℃)",
        "RN1": "1시간 강수량(mm)",
        "REH": "습도(%)",
        "PTY": "강수형태",
        "WSD": "풍속(m/s)",
    }
    pty_map = {
        "0": "없음", "1": "비", "2": "비/눈", "3": "눈",
        "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림",
    }

    results = []
    for item in items:
        cat = item["category"]
        val = item["obsrValue"]
        if cat in category_names:
            if cat == "PTY":
                val = pty_map.get(str(val), val)
            results.append(f"{category_names[cat]}: {val}")

    return f"기준시각: {base_date} {base_time} | " + ", ".join(results)


all_tools = [register_profile, save_likes, save_dislikes, get_user_profile, get_current_weather]
