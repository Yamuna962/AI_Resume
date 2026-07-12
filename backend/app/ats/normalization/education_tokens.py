"""Education degree normalization, field extraction, and matching."""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# DEGREE LEVEL ALIASES  →  canonical level string
# ---------------------------------------------------------------------------
DEGREE_ALIASES: dict[str, str] = {
    # ── Bachelor ─────────────────────────────────────────────────────────────
    "bachelor": "bachelors",
    "bachelors": "bachelors",
    "bachelor's": "bachelors",
    "bachelors degree": "bachelors",
    "bachelor degree": "bachelors",
    "bachelor of science": "bachelors",
    "bachelor of arts": "bachelors",
    "bachelor of technology": "bachelors",
    "bachelor of engineering": "bachelors",
    "bachelor of commerce": "bachelors",
    "bachelor of computer applications": "bachelors",
    "bachelor of business administration": "bachelors",
    "bachelor of laws": "bachelors",
    "bachelor of pharmacy": "bachelors",
    "bachelor of medicine": "bachelors",
    "bs": "bachelors",
    "b.s": "bachelors",
    "b.s.": "bachelors",
    "ba": "bachelors",
    "b.a": "bachelors",
    "b.a.": "bachelors",
    "btech": "bachelors",
    "b.tech": "bachelors",
    "b tech": "bachelors",
    "b.tech.": "bachelors",
    "be": "bachelors",
    "b.e": "bachelors",
    "b.e.": "bachelors",
    "beng": "bachelors",
    "bsc": "bachelors",
    "b.sc": "bachelors",
    "b.sc.": "bachelors",
    "b.com": "bachelors",
    "b.com.": "bachelors",
    "bcom": "bachelors",
    "b com": "bachelors",
    "bca": "bachelors",
    "b.ca": "bachelors",
    "b.c.a": "bachelors",
    "b.c.a.": "bachelors",
    "bba": "bachelors",
    "b.b.a": "bachelors",
    "b.b.a.": "bachelors",
    "bpharm": "bachelors",
    "b.pharm": "bachelors",
    "b.pharm.": "bachelors",
    "llb": "bachelors",
    "ll.b": "bachelors",
    "ll.b.": "bachelors",
    "undergraduate": "bachelors",
    "undergrad": "bachelors",
    "ug": "bachelors",
    # ── Master ───────────────────────────────────────────────────────────────
    "master": "masters",
    "masters": "masters",
    "master's": "masters",
    "masters degree": "masters",
    "master degree": "masters",
    "master of science": "masters",
    "master of arts": "masters",
    "master of technology": "masters",
    "master of engineering": "masters",
    "master of business administration": "masters",
    "master of computer applications": "masters",
    "master of commerce": "masters",
    "master of laws": "masters",
    "master of computer science": "masters",
    "master of information technology": "masters",
    "ms": "masters",
    "m.s": "masters",
    "m.s.": "masters",
    "ma": "masters",
    "m.a": "masters",
    "m.a.": "masters",
    "mba": "masters",
    "m.b.a": "masters",
    "m.b.a.": "masters",
    "mtech": "masters",
    "m.tech": "masters",
    "m tech": "masters",
    "m.tech.": "masters",
    "me": "masters",
    "m.e": "masters",
    "m.e.": "masters",
    "msc": "masters",
    "m.sc": "masters",
    "m.sc.": "masters",
    "mcom": "masters",
    "m.com": "masters",
    "m.com.": "masters",
    "m com": "masters",
    "mca": "masters",
    "m.c.a": "masters",
    "m.c.a.": "masters",
    "m ca": "masters",
    "mba (finance)": "masters",
    "mba (marketing)": "masters",
    "mba (hr)": "masters",
    "mba (operations)": "masters",
    "llm": "masters",
    "ll.m": "masters",
    "ll.m.": "masters",
    "mpharm": "masters",
    "m.pharm": "masters",
    "postgraduate": "masters",
    "post graduate": "masters",
    "pg": "masters",
    "graduate degree": "masters",
    # ── Doctorate ────────────────────────────────────────────────────────────
    "phd": "doctorate",
    "ph.d": "doctorate",
    "ph.d.": "doctorate",
    "doctorate": "doctorate",
    "doctoral": "doctorate",
    "doctor of philosophy": "doctorate",
    "doctor of medicine": "doctorate",
    "md": "doctorate",
    "d.phil": "doctorate",
    # ── Associates ───────────────────────────────────────────────────────────
    "associate": "associates",
    "associates": "associates",
    "associate degree": "associates",
    "associate of science": "associates",
    "associate of arts": "associates",
    "as": "associates",
    "a.s": "associates",
    "aa": "associates",
    "a.a": "associates",
    # ── Diploma ──────────────────────────────────────────────────────────────
    "diploma": "diploma",
    "pg diploma": "diploma",
    "post graduate diploma": "diploma",
    "postgraduate diploma": "diploma",
    "pgdm": "diploma",
    "pgdba": "diploma",
    "advanced diploma": "diploma",
    # ── High School ──────────────────────────────────────────────────────────
    "high school": "high_school",
    "ged": "high_school",
    "secondary school": "high_school",
    "hsc": "high_school",
    "ssc": "high_school",
    "12th": "high_school",
    "10+2": "high_school",
}

# ---------------------------------------------------------------------------
# FIELD OF STUDY ALIASES  →  canonical field
# ---------------------------------------------------------------------------
FIELD_ALIASES: dict[str, str] = {
    "cs": "computer science",
    "cse": "computer science",
    "comp sci": "computer science",
    "computer engineering": "computer science",
    "software engineering": "computer science",
    "information technology": "information technology",
    "it": "information technology",
    "ece": "electrical engineering",
    "eee": "electrical engineering",
    "ee": "electrical engineering",
    "mechanical engineering": "mechanical engineering",
    "civil engineering": "civil engineering",
    "data science": "data science",
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
    "machine learning": "machine learning",
    "business administration": "business administration",
    "commerce": "commerce",
    "b.com": "commerce",
    "m.com": "commerce",
    "finance": "finance",
    "accounting": "accounting",
    "economics": "economics",
    "mathematics": "mathematics",
    "math": "mathematics",
    "statistics": "statistics",
    "physics": "physics",
    "chemistry": "chemistry",
    "biology": "biology",
    "computer applications": "computer applications",
    "mca": "computer applications",
    "bca": "computer applications",
    "pharmacy": "pharmacy",
    "law": "law",
    "psychology": "psychology",
    "management": "management",
    "operations management": "management",
    "hr": "human resources",
    "human resources": "human resources",
    "marketing": "marketing",
}

# ---------------------------------------------------------------------------
# LEVEL HIERARCHY  — higher level satisfies a lower requirement
# ---------------------------------------------------------------------------
LEVEL_RANK: dict[str, int] = {
    "high_school": 1,
    "diploma": 2,
    "associates": 3,
    "bachelors": 4,
    "masters": 5,
    "doctorate": 6,
}

# ---------------------------------------------------------------------------
# FIELD RELATION GROUPS  — fields treated as equivalent for matching
# ---------------------------------------------------------------------------
_RELATED_FIELD_GROUPS: list[set[str]] = [
    {"computer science", "software engineering", "information technology",
     "data science", "computer applications", "artificial intelligence"},
    {"electrical engineering", "electronics", "ece"},
    {"finance", "accounting", "commerce", "business administration", "management", "economics"},
    {"mechanical engineering", "civil engineering"},
    {"pharmacy", "biology", "chemistry"},
    {"law"},
    {"marketing", "human resources", "management"},
]

_DEGREE_PATTERN = re.compile(
    r"(?i)\b("
    r"b\.?\s*tech\.?|b\.?\s*e\.?|b\.?\s*s\.?c?\.?|b\.?\s*a\.?|b\.?\s*com\.?|b\.?\s*ca\.?|b\.?\s*b\.?\s*a\.?|"
    r"m\.?\s*tech\.?|m\.?\s*e\.?|m\.?\s*s\.?c?\.?|m\.?\s*a\.?|m\.?\s*b\.?\s*a\.?|m\.?\s*com\.?|m\.?\s*ca\.?|"
    r"ph\.?\s*d\.?|bachelor(?:'s)?|master(?:'s)?|doctorate|doctoral|"
    r"associate(?:'s)?|diploma|undergraduate|postgraduate|ged|"
    r"mba|mca|bca|bba|pgdm"
    r")\b"
)

_FIELD_PATTERN = re.compile(
    r"(?i)\b(?:in|of)\s+"
    r"([A-Za-z][A-Za-z\s&/\-]{2,40}?"
    r"(?:\s+or\s+related\s+field)?)"
    r"(?:\s*(?:degree|from|at|,|\d{4}|$))",
)
_MOS_PATTERN = re.compile(
    r"(?i)\bmaster\s+of\s+(?:science|arts|engineering|technology|commerce|computer|business)\s+in\s+([A-Za-z][A-Za-z\s&/\-]{2,40})"
)

_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

_INSTITUTION_PATTERN = re.compile(
    r"(?i)\b(?:from|at)\s+([A-Z][A-Za-z\s&\-']{3,50}?)(?:\s*(?:\d{4}|,|$))"
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip()).strip(".,;:")


def normalize_degree_name(text: str) -> str:
    """
    Normalize any degree name/abbreviation to a standard canonical form.
    Supports: Bachelor Degree, Master Degree, MBA, MCA, B.Tech, B.E, B.Sc, B.Com, M.Tech, Diploma, Associate Degree
    """
    t = text.lower().strip().replace(".", "")
    if "btech" in t or "b tech" in t or "bachelor of technology" in t:
        return "B.Tech"
    if "mtech" in t or "m tech" in t or "master of technology" in t:
        return "M.Tech"
    if "bcom" in t or "b com" in t or "bachelor of commerce" in t or "bachelors in commerce" in t:
        return "B.Com"
    if "mca" in t or "master of computer applications" in t:
        return "MCA"
    if "mba" in t or "master of business administration" in t:
        return "MBA"
    if "bsc" in t or "b sc" in t or "bachelor of science" in t:
        return "B.Sc"
    if "beng" in t or "b e" in t or "bachelor of engineering" in t or t == "be":
        return "B.E"
    if "associate" in t:
        return "Associate Degree"
    if "diploma" in t or "pgdm" in t or "pgdba" in t:
        return "Diploma"
    if "bachelor" in t or t.startswith("bs") or t.startswith("ba") or t == "undergraduate" or t == "undergrad":
        return "Bachelor Degree"
    if "master" in t or t.startswith("ms") or t.startswith("ma") or t == "postgraduate":
        return "Master Degree"
    if "phd" in t or "doctor" in t:
        return "Doctorate"
    return text.title()


def canonical_degree_level(text: str) -> str | None:
    """Extract canonical degree level from free text."""
    if not text:
        return None
    t = _clean(text)

    # Direct alias lookup on full text
    if t in DEGREE_ALIASES:
        return DEGREE_ALIASES[t]

    # Token-by-token lookup
    for token in re.split(r"[\s,/\-]+", t):
        token = token.strip(".")
        if token in DEGREE_ALIASES:
            return DEGREE_ALIASES[token]

    # Regex pattern match
    for match in _DEGREE_PATTERN.finditer(text):
        key = _clean(match.group(0))
        if key in DEGREE_ALIASES:
            return DEGREE_ALIASES[key]
        compact = re.sub(r"[\s.]+", "", key)
        if compact in DEGREE_ALIASES:
            return DEGREE_ALIASES[compact]

    # Keyword fallbacks
    if "bachelor" in t or "undergrad" in t or "b.tech" in t or "btech" in t:
        return "bachelors"
    if "master" in t or "mba" in t or "mca" in t or "postgrad" in t:
        return "masters"
    if "phd" in t or "doctor" in t:
        return "doctorate"
    if "associate" in t:
        return "associates"
    if "diploma" in t or "pgdm" in t or "pgdba" in t:
        return "diploma"
    if "high school" in t or "ged" in t or "hsc" in t or "ssc" in t:
        return "high_school"
    return None


def canonical_field(text: str) -> str | None:
    """Extract canonical field of study from degree line."""
    if not text:
        return None
    t = _clean(text)

    # ── Generic / meaningless field terms that should be treated as "no field" ──
    _GENERIC_FIELDS = {
        "relevant field", "related field", "any field", "any discipline",
        "relevant discipline", "equivalent", "higher", "or higher", "similar field",
        "appropriate field", "relevant", "related", "applicable field",
    }
    if t in _GENERIC_FIELDS:
        return None

    mos = _MOS_PATTERN.search(text)
    if mos:
        field = _clean(mos.group(1))
        if field in _GENERIC_FIELDS:
            return None
        return FIELD_ALIASES.get(field, field)

    if t in FIELD_ALIASES:
        return FIELD_ALIASES[t]

    for token in re.split(r"[,/\-]", t):
        token = _clean(token)
        if token in FIELD_ALIASES:
            return FIELD_ALIASES[token]

    field_match = _FIELD_PATTERN.search(text)
    if field_match:
        field = _clean(field_match.group(1))
        field = re.sub(r"\s+or\s+related\s+field.*$", "", field).strip()
        field = re.sub(r"\s+or\s+higher.*$", "", field).strip()
        field = field.split(",")[0].strip()
        if field in _GENERIC_FIELDS or len(field) <= 3:
            return None
        return FIELD_ALIASES.get(field, field)

    # Common patterns: "B.Tech Computer Science", "BS in CS"
    for alias, canon in FIELD_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", t):
            return canon

    # Extract longest meaningful phrase after degree abbreviation
    stripped = re.sub(
        r"(?i)\b(b\.?\s*tech|b\.?\s*e|b\.?\s*s|b\.?\s*com|b\.?\s*ca|b\.?\s*b\.?\s*a|"
        r"m\.?\s*s|m\.?\s*tech|m\.?\s*com|m\.?\s*ca|m\.?\s*b\.?\s*a|ph\.?d|"
        r"bachelor|master|associate|diploma|mba|mca|bca)\b\.?",
        "",
        text,
    )
    stripped = _clean(stripped)
    stripped = re.sub(r"\b(or\s+higher|or\s+above|and\s+above)\b", "", stripped).strip()
    stripped = stripped.split(",")[0].strip()
    stripped = re.sub(r"\b(university|college|institute|of technology|iit|nit)\b", "", stripped).strip()
    stripped = re.sub(r"\b\d{4}\b", "", stripped).strip(" ,;-")
    if stripped in _GENERIC_FIELDS or len(stripped) <= 3:
        return None
    if len(stripped) > 3:
        return FIELD_ALIASES.get(stripped, stripped)
    return None




def parse_education_line(line: str) -> dict[str, str]:
    """Parse one education line into structured fields."""
    line = line.strip()
    if not line:
        return {}

    year_match = _YEAR_PATTERN.search(line)
    year = year_match.group(0) if year_match else ""

    institution = ""
    inst_match = _INSTITUTION_PATTERN.search(line)
    if inst_match:
        institution = inst_match.group(1).strip()
    else:
        parts = re.split(r",|\d{4}", line)
        for part in parts:
            p = part.strip()
            if re.search(r"(?i)\b(university|college|institute|iit|nit|school)\b", p):
                institution = p.strip()
                break

    level = canonical_degree_level(line) or ""
    field = canonical_field(line) or ""

    return {
        "raw": line,
        "degree_level": level,
        "field": field,
        "institution": institution,
        "year": year,
        "canonical": f"{level} {field}".strip() if level or field else _clean(line),
    }


def _fields_related(jd_field: str, res_field: str) -> bool:
    """True when fields are equivalent or commonly related."""
    if jd_field == res_field:
        return True
    for group in _RELATED_FIELD_GROUPS:
        if jd_field in group and res_field in group:
            return True
    # Word-level overlap
    jd_words = set(jd_field.split()) - {"of", "in", "and", "the", "a"}
    res_words = set(res_field.split()) - {"of", "in", "and", "the", "a"}
    if jd_words and res_words and len(jd_words & res_words) >= 1:
        return True
    return False


def education_requirements_match(
    jd_req: str, resume_entries: list[dict[str, str]]
) -> tuple[float, str]:
    """
    Match one JD education requirement against resume education entries.
    """
    if not resume_entries:
        return 0.0, "no_resume_education"

    jd_level = canonical_degree_level(jd_req)
    jd_field = canonical_field(jd_req)
    jd_clean = _clean(jd_req)

    best_credit = 0.0
    best_reason = "none"

    for entry in resume_entries:
        res_level = entry.get("degree_level") or canonical_degree_level(entry.get("raw", ""))
        res_field = entry.get("field") or canonical_field(entry.get("raw", ""))
        res_raw = _clean(entry.get("raw", ""))

        credit = 0.0
        reason = ""

        jd_rank = LEVEL_RANK.get(jd_level, 0) if jd_level else 0
        res_rank = LEVEL_RANK.get(res_level, 0) if res_level else 0

        # ── Case 1: JD specifies level + field ───────────────────────────────
        if jd_level and res_level and jd_field and res_field:
            field_ok = _fields_related(jd_field, res_field)
            if res_rank >= jd_rank and field_ok:
                credit = max(credit, 1.0)
                reason = "level_and_field_met"
            elif res_rank >= jd_rank:
                credit = max(credit, 0.90)
                reason = "level_met_field_different"
            elif field_ok and res_rank == jd_rank - 1:
                credit = max(credit, 0.60)
                reason = "field_met_level_close"

        # ── Case 2: JD specifies level only (generic "Bachelor's Degree") ────
        elif jd_level and res_level and not jd_field:
            if res_rank >= jd_rank:
                credit = max(credit, 1.0)        # Level fully satisfied
                reason = "level_only_met"
            elif res_rank == jd_rank - 1:
                credit = max(credit, 0.50)
                reason = "level_one_below"

        # ── Case 3: JD specifies field only (rare) ───────────────────────────
        elif jd_field and res_field:
            field_ok = _fields_related(jd_field, res_field)
            if field_ok:
                credit = max(credit, 0.90 if jd_level else 0.85)
                reason = "field_met"
            elif any(w in res_field for w in jd_field.split() if len(w) > 3):
                credit = max(credit, 0.75)
                reason = "field_partial"

        # ── Case 4: Level-only match regardless of field ─────────────────────
        if jd_level and res_level and not credit:
            if res_rank >= jd_rank:
                credit = max(credit, 0.85)
                reason = "level_met"
            elif res_rank == jd_rank - 1:
                credit = max(credit, 0.45)
                reason = "level_close"

        # ── Case 5: Substring / token overlap on full text ───────────────────
        if jd_clean and res_raw:
            if jd_clean in res_raw or res_raw in jd_clean:
                credit = max(credit, 0.90)
                reason = "text_exact"
            else:
                jd_tokens = set(jd_clean.split()) - {
                    "in", "of", "a", "an", "the", "degree", "or", "and", "related", "field"
                }
                res_tokens = set(res_raw.split())
                overlap = len(jd_tokens & res_tokens)
                if overlap >= 2:
                    credit = max(credit, min(0.80, overlap / max(len(jd_tokens), 1)))
                    reason = "token_overlap"
                elif overlap == 1 and len(jd_tokens) <= 2:
                    credit = max(credit, 0.60)
                    reason = "token_partial"

        if credit > best_credit:
            best_credit = credit
            best_reason = reason

    return best_credit, best_reason


def mine_education_from_text(text: str) -> list[str]:
    """Extract education requirement lines from JD body when no section header."""
    found: list[str] = []
    patterns = [
        re.compile(
            r"(?i)(?:"
            r"(?:bachelor|master|associate|ph\.?d|b\.?\s*tech|m\.?\s*tech|diploma|mba|mca|b\.?\s*com)"
            r"[^.\n]{0,80}?(?:degree|in|of)[^.\n]{0,60}"
            r")"
        ),
        re.compile(
            r"(?i)(?:minimum|required)?\\s*education\\s*[:\\-]?\\s*([^\\n.]{10,80})"
        ),
        re.compile(
            r"(?i)(\\d+\\s*years?[^.\\n]{0,30}(?:bachelor|master|degree)[^.\\n]{0,60})"
        ),
    ]
    for pat in patterns:
        for match in pat.finditer(text):
            line = match.group(0).strip() if match.lastindex is None else match.group(1).strip()
            if line and len(line) > 8:
                found.append(line)
    return list(dict.fromkeys(found))
