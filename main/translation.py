"""Fill empty English fields from Arabic using Google Translate (via deep-translator)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def translate_ar_to_en(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator

        result = GoogleTranslator(source="ar", target="en").translate(text)
        return (result or "").strip()
    except Exception:
        logger.exception("Arabic→English translation failed")
        return text  # fallback: keep Arabic so required fields are not empty


def fill_empty_en_from_ar(obj) -> list[str]:
    """
    For every model field ending in _ar, if the matching _en field is empty,
    translate Arabic into English. Returns list of filled field names (en side).
    """
    filled: list[str] = []
    field_names = {f.name for f in obj._meta.get_fields() if hasattr(f, "attname")}

    for ar_name in sorted(n for n in field_names if n.endswith("_ar")):
        en_name = ar_name[:-3] + "_en"
        if en_name not in field_names:
            continue

        ar_val = getattr(obj, ar_name, None)
        en_val = getattr(obj, en_name, None)
        if not (isinstance(ar_val, str) and ar_val.strip()):
            continue
        if isinstance(en_val, str) and en_val.strip():
            continue

        translated = translate_ar_to_en(ar_val)
        if translated:
            setattr(obj, en_name, translated)
            filled.append(en_name)

    return filled
