import json
import os
import threading

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
_lock = threading.Lock()


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_user(user_id: str, age: int, gender: str):
    with _lock:
        data = _load()
        existing = data.get(user_id, {})
        existing.update({"age": age, "gender": gender})
        data[user_id] = existing
        _save(data)


def save_preferences(user_id: str, likes: list[str] = None, dislikes: list[str] = None):
    with _lock:
        data = _load()
        if user_id not in data:
            data[user_id] = {}
        if likes is not None:
            data[user_id]["likes"] = likes
        if dislikes is not None:
            data[user_id]["dislikes"] = dislikes
        _save(data)


def get_user(user_id: str) -> dict | None:
    with _lock:
        data = _load()
        return data.get(user_id)
