"""Domain inference from job title, skills, and resume content."""
from __future__ import annotations

import re

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "software": (
        "software", "developer", "engineer", "backend", "frontend", "full stack",
        "fullstack", "web", "api", "microservices", "devops", "sre",
    ),
    "ai_ml": (
        "machine learning", "deep learning", "nlp", "computer vision", "llm",
        "generative ai", "genai", "neural", "pytorch", "tensorflow", "rag",
        "transformer", "hugging face", "large language model",
    ),
    "data_science": (
        "data scientist", "data science", "analytics", "statistics", "pandas",
        "numpy", "tableau", "power bi", "sql", "etl", "data analyst",
    ),
    "erp": (
        "sap", "oracle erp", "netsuite", "dynamics", "erp", "workday",
        "peoplesoft", "general ledger", "accounts payable", "accounts receivable",
    ),
    "compliance": (
        "aml", "kyc", "cdd", "edd", "anti money laundering", "know your customer",
        "customer due diligence", "enhanced due diligence", "transaction monitoring",
        "sanctions", "ofac", "fatf", "bsa", "financial crime", "financial crime compliance",
        "suspicious activity", "sar", "pep", "name screening", "adverse media",
        "risk based approach", "correspondent banking", "de-risking", "compliance officer",
        "regulatory compliance", "fca", "cams", "cfcs",
    ),
    "banking": (
        "banking", "core banking", "payments", "loan", "mortgage",
        "treasury", "swift", "fintech", "neft", "rtgs", "imps", "upi", "sepa",
        "wire transfer", "credit", "retail banking", "investment banking",
    ),
    "finance": (
        "finance", "accounting", "audit", "tax", "fp&a", "financial analyst",
        "cfa", "cpa", "gaap", "ifrs", "budgeting", "forecasting", "financial planning",
        "financial modeling", "variance analysis", "management reporting", "acca", "frm",
    ),
    "risk": (
        "operational risk", "credit risk", "market risk", "risk assessment", "risk management",
        "risk analyst", "risk officer", "enterprise risk", "liquidity risk",
        "model risk", "cyber risk", "risk framework",
    ),
    "healthcare": (
        "healthcare", "clinical", "hipaa", "ehr", "emr", "patient", "medical",
        "pharma", "fda", "hl7", "fhir",
    ),
    "marketing": (
        "marketing", "seo", "sem", "campaign", "brand", "content marketing",
        "social media", "crm", "hubspot", "google ads",
    ),
    "corporate": (
        "manager", "consultant", "operations", "project manager", "business analyst",
        "stakeholder", "strategy", "leadership",
    ),
}


def infer_domain(text: str) -> str:
    """Return best-fit domain label from free text."""
    if not text:
        return "general"

    lower = text.lower()
    scores: dict[str, int] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        hit = sum(1 for kw in keywords if kw in lower)
        if hit:
            scores[domain] = hit

    if not scores:
        return "general"

    best = max(scores, key=scores.get)
    return best.replace("_", " ")


def normalize_domain_label(domain: str) -> str:
    """Normalize domain string to canonical label."""
    if not domain:
        return "general"
    cleaned = re.sub(r"[_\-]+", " ", domain.strip().lower())
    for key in _DOMAIN_KEYWORDS:
        if key.replace("_", " ") == cleaned or key == cleaned:
            return key.replace("_", " ")
    return cleaned or "general"
