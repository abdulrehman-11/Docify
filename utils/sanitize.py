import re
from typing import List

# Maps spelled-out numbers to digits for email handling.
NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def _collapse_spelled_letters(tokens: List[str]) -> List[str]:
    """
    Collapse contiguous single-letter tokens into a single word.
    Example: ["k","a","t","h","i","e","smith"] -> ["kathie", "smith"]
    """
    out: List[str] = []
    buffer: List[str] = []

    def flush():
        nonlocal buffer
        if buffer:
            out.append("".join(buffer))
            buffer = []

    for tok in tokens:
        if len(tok) == 1 and tok.isalpha():
            buffer.append(tok)
        else:
            flush()
            if tok:
                out.append(tok)

    flush()
    return out


def sanitize_name(raw: str) -> str:
    """
    Deterministically join spelled letters; avoid LLM normalization.
    - Lowercases then Title-cases words.
    - Collapses single-letter sequences into words.
    """
    if not raw:
        return raw
    tokens = re.split(r"\s+", raw.strip().lower())
    collapsed = _collapse_spelled_letters(tokens)
    # Title-case each word (keeps inner casing simple)
    return " ".join(word.title() for word in collapsed if word)


def sanitize_email(raw: str) -> str:
    """
    Deterministic email sanitizer:
    - Lowercase
    - Replace spoken 'at'/'dot'
    - Convert number words to digits
    - Remove spaces
    - Strip invalid characters
    """
    if not raw:
        return raw
    cleaned = raw.strip().lower()
    # Tokenize on whitespace to safely replace words
    tokens = re.split(r"\s+", cleaned)
    norm_tokens: List[str] = []
    for tok in tokens:
        if tok in NUMBER_WORDS:
            norm_tokens.append(NUMBER_WORDS[tok])
        elif tok in {"at", "(at)"}:
            norm_tokens.append("@")
        elif tok in {"dot", "dots"}:
            norm_tokens.append(".")
        else:
            norm_tokens.append(tok)
    merged = "".join(norm_tokens)
    # Remove common spoken fillers and invalid chars
    merged = merged.replace("(", "").replace(")", "").replace(",", "").replace(";", "")
    merged = re.sub(r"[^a-z0-9._%+\-@]+", "", merged)
    return merged

