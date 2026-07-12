import re
from typing import Any


def clean_text(text: str) -> str:
    """Removes extra whitespace and special characters."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\.,;:\-\(\)\/\&\#\+]", "", text)
    return text.strip()


def normalize_skills(skills_list: list[str]) -> list[str]:
    """Lowercases and strips skills for matching."""
    return [skill.strip().lower() for skill in skills_list if skill.strip()]


def extract_resume_skill_text(resume_sections: dict[str, str], fallback: str = "") -> str:
    """Combine all skill-bearing resume sections (domain-agnostic)."""
    parts = [
        resume_sections.get("skills", ""),
        resume_sections.get("experience", ""),
        resume_sections.get("projects", ""),
        resume_sections.get("certifications", ""),
    ]
    combined = " ".join(p.strip() for p in parts if p.strip())
    return combined or fallback


# Multi-word phrases preserved during keyword extraction (cross-domain)
_MULTI_WORD_PHRASES = [
    # Tech / Developer
    "machine learning", "deep learning", "full stack", "full-stack", "front end", "frontend",
    "back end", "backend", "node.js", "react.js", "vue.js", "next.js", "express.js",
    "rest api", "rest apis", "graphql", "microservices", "cloud computing",
    "continuous integration", "continuous deployment", "ci/cd", "devops",
    "data structures", "object oriented", "test driven", "unit testing",
    "amazon web services", "google cloud", "microsoft azure",
    # ERP / Finance (kept for mixed use)
    "dynamics 365", "d365 f&o", "finance & operations", "finance and operations",
    "general ledger", "accounts payable", "accounts receivable", "procure-to-pay",
    "data management framework",
    # Sales / Business
    "lead generation", "pipeline management", "customer relationship management",
    "b2b sales", "b2c sales", "saas sales", "account management",
    "business development", "cold calling", "closing deals",
    "salesforce", "hubspot", "customer success",
    # General professional
    "project management", "agile", "scrum", "kanban", "stakeholder management",
    "cross functional", "problem solving", "user acceptance testing",
    "system integration testing", "azure devops", "power bi",
]

# Valid short tokens across domains (len <= 3)
_ALLOWED_SHORT_TOKENS = {
    "js", "ts", "go", "sql", "api", "css", "html", "aws", "gcp", "dev", "seo",
    "crm", "b2b", "b2c", "ui", "ux", "ml", "ai", "ci", "cd", "erp", "fo",
    "gl", "ap", "ar", "p2p", "dmf", "uat", "sit", "fdd", "frd", "sdd",
    "c++", "c#", ".net",
}

# Generic JD noise — not job requirements
_JD_NOISE_WORDS = {
    "location", "remote", "hybrid", "onsite", "description", "employment",
    "full-time", "part-time", "contract", "summary", "looking", "candidate",
    "join", "team", "company", "organization", "opportunity", "position",
    "title", "salary", "benefits", "equal", "employer", "apply", "applying",
    "bengaluru", "bangalore", "hyderabad", "mumbai", "delhi", "chennai", "pune",
    "india", "usa", "united", "states",
}

_JD_SECTION_PATTERNS = {
    "required_skills": r"(?i)(required\s+skills|key\s+skills|requirements|qualifications|must[\-\s]have|what\s+you(?:'ll|\s+will)\s+need|technical\s+skills)",
    "preferred_skills": r"(?i)(preferred\s+qualifications|preferred\s+skills|nice[\-\s]to[\-\s]have|good\s+to\s+have|bonus\s+points)",
    "responsibilities": r"(?i)(key\s+responsibilities|responsibilities|what\s+you(?:'ll|\s+will)\s+do|duties|role\s+overview)",
}

_COMPILED_PHRASES = [
    (p, re.compile(r"\b" + re.escape(p) + r"\b", re.IGNORECASE))
    for p in _MULTI_WORD_PHRASES
]


def _extract_section_text(text: str, start_pattern: str, stop_patterns: list[str]) -> str:
    start_match = re.search(start_pattern, text)
    if not start_match:
        return ""
    start_pos = start_match.end()
    end_pos = len(text)
    for stop_pat in stop_patterns:
        stop_match = re.search(stop_pat, text[start_pos:])
        if stop_match:
            end_pos = min(end_pos, start_pos + stop_match.start())
    return text[start_pos:end_pos].strip()


def parse_job_description(jd_text: str) -> dict[str, Any]:
    """Extract structured sections from any job description."""
    other = [p for k, p in _JD_SECTION_PATTERNS.items()]

    required_text = _extract_section_text(
        jd_text, _JD_SECTION_PATTERNS["required_skills"],
        [p for k, p in _JD_SECTION_PATTERNS.items() if k != "required_skills"],
    )
    preferred_text = _extract_section_text(
        jd_text, _JD_SECTION_PATTERNS["preferred_skills"],
        [p for k, p in _JD_SECTION_PATTERNS.items() if k != "preferred_skills"],
    )
    responsibilities_text = _extract_section_text(
        jd_text, _JD_SECTION_PATTERNS["responsibilities"],
        [p for k, p in _JD_SECTION_PATTERNS.items() if k != "responsibilities"],
    )

    required_skills = extract_keywords(required_text, for_jd=True) if required_text else []
    preferred_skills = extract_keywords(preferred_text, for_jd=True) if preferred_text else []

    if not required_skills:
        required_skills = extract_keywords(jd_text, for_jd=True)

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "required_skills_text": required_text or jd_text,
        "responsibilities": responsibilities_text,
        "responsibilities_text": responsibilities_text,
        "experience_level": "",
    }


def extract_keywords(text: str, for_jd: bool = False) -> list[str]:
    """Domain-aware keyword extraction with multi-word phrase support."""
    found_phrases: set[str] = set()
    remaining_text = text

    for phrase, pattern in _COMPILED_PHRASES:
        if pattern.search(remaining_text):
            found_phrases.add(phrase.lower())
            remaining_text = pattern.sub(" ", remaining_text)

    remaining_clean = re.sub(r"[^\w\s#+]", " ", remaining_text.lower())
    single_words: set[str] = set()
    for w in remaining_clean.split():
        token = w.strip()
        if not token or token in _STOP_WORDS:
            continue
        if for_jd and token in _JD_NOISE_WORDS:
            continue
        if token in _ALLOWED_SHORT_TOKENS or len(token) > 3:
            single_words.add(token)

    keywords = list(found_phrases | single_words)
    if for_jd:
        keywords = [k for k in keywords if k not in _JD_NOISE_WORDS]
    return keywords


_STOP_WORDS = {
    "with", "that", "this", "from", "have", "been", "will", "they",
    "their", "your", "about", "which", "when", "there", "where",
    "some", "such", "other", "more", "very", "also", "must", "well",
    "able", "both", "each", "into", "than", "then", "them", "what",
    "should", "would", "could", "include", "including", "related",
    "relevant", "required", "strong", "good", "work", "team", "years",
    "year", "least", "across", "within", "between", "through",
    "hands", "using", "basis", "level", "degree", "role", "roles",
    "client", "clients", "ensure", "support", "system", "systems",
    "tools", "tool", "working", "experience", "knowledge", "skill",
    "skills", "ability", "manage", "design", "analysis", "data",
    "looking", "closely", "business", "perform", "provide", "collaborate",
    "gather", "prepare", "configure", "implement", "successful", "delivery",
}
