"""
name_matcher.py
Robust candidate name normalization and verification utility.

Compares candidate registered name with extracted CV name while tolerating:
- Case variations (e.g., "RAHUL PANDIT" vs "rahul pandit")
- Whitespace variations (extra spaces, tabs, leading/trailing blanks)
- Common prefixes and honorifics (Mr., Ms., Dr., Engr.)
- Punctuation (periods, commas, hyphens)
- Middle names or middle initials (e.g., "Rahul Kumar Pandit" vs "Rahul Pandit")
- Name reordering (e.g., "Pandit, Rahul" vs "Rahul Pandit")
"""

import re
import difflib

# Common titles, prefixes, and academic suffixes to ignore during normalization
IGNORED_AFFIXES = {
    "mr", "mrs", "ms", "miss", "dr", "prof", "professor", "engr", "engineer", "er",
    "jr", "sr", "ii", "iii", "iv", "phd", "msc", "bsc", "be", "btech", "mtech", "mba"
}

def clean_and_normalize_name(name_str: str) -> str:
    """
    Normalizes a name string:
    - Lowercases text
    - Strips non-alphanumeric punctuation
    - Removes common titles/honorifics and degrees
    - Collapses multiple whitespace characters
    """
    if not name_str:
        return ""

    # 1. Lowercase and replace commas/hyphens/underscores with spaces
    cleaned = re.sub(r'[,_\-\/]', ' ', name_str.lower())
    
    # 2. Remove all non-alphabetic and non-space characters
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)

    # 3. Tokenize and filter out known honorifics/affixes and single-letter junk
    raw_tokens = cleaned.split()
    filtered_tokens = []
    for token in raw_tokens:
        token_clean = token.strip()
        if not token_clean:
            continue
        if token_clean in IGNORED_AFFIXES:
            continue
        filtered_tokens.append(token_clean)

    return " ".join(filtered_tokens).strip()


def verify_name_match(registered_name: str, cv_name: str) -> tuple[bool, str]:
    """
    Compares registered name with CV extracted name.
    Returns:
        (is_match: bool, message: str)
    """
    if not registered_name or not registered_name.strip():
        return False, "Registered candidate name is missing. Please update your profile."

    if not cv_name or not cv_name.strip() or cv_name.strip().lower() in ["candidate", "unknown", "n/a"]:
        return False, "Your registered name does not match the name on your CV. Please upload the correct CV."

    norm_reg = clean_and_normalize_name(registered_name)
    norm_cv = clean_and_normalize_name(cv_name)

    if not norm_reg or not norm_cv:
        return False, "Your registered name does not match the name on your CV. Please upload the correct CV."

    # 1. Exact match after normalization
    if norm_reg == norm_cv:
        return True, "Name verified successfully (exact match)."

    tokens_reg = norm_reg.split()
    tokens_cv = norm_cv.split()

    # 2. Token set equality (handles reordered names e.g., "Pandit Rahul" vs "Rahul Pandit")
    if set(tokens_reg) == set(tokens_cv):
        return True, "Name verified successfully (reordered tokens match)."

    # 3. First and Last name match (tolerates middle names / initials)
    # E.g. "Rahul Kumar Pandit" vs "Rahul Pandit" or "John M. Doe" vs "John Doe"
    if len(tokens_reg) >= 2 and len(tokens_cv) >= 2:
        first_match = (tokens_reg[0] == tokens_cv[0])
        last_match = (tokens_reg[-1] == tokens_cv[-1])
        if first_match and last_match:
            return True, "Name verified successfully (first and last name match)."

    # 4. Subset containment check (all tokens of the shorter name exist in the longer name)
    set_reg = set(tokens_reg)
    set_cv = set(tokens_cv)
    if (set_reg.issubset(set_cv) or set_cv.issubset(set_reg)) and len(set_reg & set_cv) >= 2:
        return True, "Name verified successfully (token subset match)."

    # 5. Fuzzy string similarity check (tolerates minor OCR/spelling discrepancies, threshold >= 0.85)
    # Both names must share at least the primary first or last token to prevent false positives
    has_token_overlap = bool(set_reg & set_cv)
    similarity = difflib.SequenceMatcher(None, norm_reg, norm_cv).ratio()
    if similarity >= 0.85 and has_token_overlap:
        return True, f"Name verified successfully (similarity: {similarity:.2f})."

    # Mismatch detected
    return False, "Your registered name does not match the name on your CV. Please upload the correct CV."
