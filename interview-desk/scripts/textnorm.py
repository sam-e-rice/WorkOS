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


def same_person(label: str, name: str) -> bool:
    """Transcript label vs calendar name: exact, or same first name ("Jane" vs "Jane Doe")."""
    a, b = norm(label).split(), norm(name).split()
    return bool(a and b) and (a == b or a[0] == b[0])
