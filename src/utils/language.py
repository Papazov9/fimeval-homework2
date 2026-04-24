_CODE_TO_FULL = {
    "en": "English",
    "bg": "Bulgarian",
    "zh": "Chinese",
    "hr": "Croatian",
    "it": "Italian",
    "sr": "Serbian",
}
_FULL_LOWER_TO_FULL = {v.lower(): v for v in _CODE_TO_FULL.values()}


def to_full_language(lang: str) -> str:
    if not lang:
        return "unknown"
    key = lang.strip().lower()
    if key in _CODE_TO_FULL:
        return _CODE_TO_FULL[key]
    if key in _FULL_LOWER_TO_FULL:
        return _FULL_LOWER_TO_FULL[key]
    return lang
