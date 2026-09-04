import re
import unicodedata

# Words that get stripped out when building the "normalized" comparison key,
# so "Abune Petros School" and "Abune Petros" collide, and "St. Mary's Church"
# and "Saint Mary Church" collide. Keep this list small and boring —
# aggressive stripping causes false-positive collisions between genuinely
# different orgs.
_NOISE_WORDS = {
    "the", "school", "church", "academy", "college", "institute",
    "parish", "congregation", "ministries", "ministry", "of", "and",
}

_ABBREVIATIONS = {
    "st": "saint",
    "st.": "saint",
    "mt": "mount",
    "mt.": "mount",
}


def normalize_org_name(name: str) -> str:
    """
    Produce a comparison key for exact-duplicate detection.
    NOT what's displayed or stored as the org's real name — only used
    for the unique constraint / duplicate check.
    """
    if not name:
        return ""

    # Strip accents/diacritics, lowercase
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()

    # Drop possessives and punctuation
    text = text.replace("'s", "").replace("’s", "")
    text = re.sub(r"[^\w\s]", " ", text)

    # Expand common abbreviations, drop noise words
    tokens = text.split()
    tokens = [_ABBREVIATIONS.get(t, t) for t in tokens]
    tokens = [t for t in tokens if t not in _NOISE_WORDS]

    normalized = " ".join(sorted(tokens))  # order-independent
    return normalized.strip()


def sanitize_org_name(name: str) -> str:
    """Basic input sanitization for the display name (not the compare key)."""
    if not name:
        return ""
    # Strip any HTML/script content defensively; org names are plain text.
    text = re.sub(r"<[^>]*>", "", name)
    text = re.sub(r"\s+", " ", text).strip()
    return text
