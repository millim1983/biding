# app/core/preferences.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from app.core.config import BASE_DIR  # config.py에서 BASE_DIR 이미 쓴 거 재사용

DATA_DIR = BASE_DIR / "data"
PREF_PATH = DATA_DIR / "preferences.json"


@dataclass
class Preferences:
    keywords: List[str]
    orgs: List[str]

    @classmethod
    def empty(cls) -> "Preferences":
        return cls(keywords=[], orgs=[])


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_preferences() -> Preferences:
    _ensure_data_dir()
    if not PREF_PATH.exists():
        return Preferences.empty()

    try:
        with PREF_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return Preferences(
            keywords=raw.get("keywords", []),
            orgs=raw.get("orgs", []),
        )
    except Exception:
        # 파일이 깨졌거나 하면 초기화
        return Preferences.empty()


def save_preferences(prefs: Preferences) -> None:
    _ensure_data_dir()
    with PREF_PATH.open("w", encoding="utf-8") as f:
        json.dump(asdict(prefs), f, ensure_ascii=False, indent=2)


def add_keyword(text: str) -> Preferences:
    prefs = load_preferences()
    text = text.strip()
    if text and text not in prefs.keywords:
        prefs.keywords.append(text)
        save_preferences(prefs)
    return prefs


def delete_keyword(text: str) -> Preferences:
    prefs = load_preferences()
    prefs.keywords = [k for k in prefs.keywords if k != text]
    save_preferences(prefs)
    return prefs


def add_org(name: str) -> Preferences:
    prefs = load_preferences()
    name = name.strip()
    if name and name not in prefs.orgs:
        prefs.orgs.append(name)
        save_preferences(prefs)
    return prefs


def delete_org(name: str) -> Preferences:
    prefs = load_preferences()
    prefs.orgs = [o for o in prefs.orgs if o != name]
    save_preferences(prefs)
    return prefs
