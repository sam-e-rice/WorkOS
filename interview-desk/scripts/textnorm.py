"""Normalisation shared by quote, fact, CV and role matching."""
import re
import unicodedata


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[\W_]+", " ", s)
    return " ".join(s.split())


def tokens(s: str) -> list[str]:
    return norm(s).split()
