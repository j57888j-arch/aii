from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES = ("uz", "ru", "en")


@lru_cache(maxsize=3)
def load_catalog(language: str) -> dict[str, Any]:
    if language not in SUPPORTED_LANGUAGES:
        language = "uz"
    path = LOCALES_DIR / f"{language}.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def translate(language: str, key: str, **values: object) -> str:
    catalog = load_catalog(language)
    fallback = load_catalog("uz")
    template = catalog.get(key, fallback.get(key, key))
    return template.format(**values)
