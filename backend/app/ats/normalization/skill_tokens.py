"""Shared skill token decomposition and alias expansion."""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# CANONICAL SKILL ALIAS MAP
# alias (lowercased) -> canonical (lowercased, display-ready)
# ---------------------------------------------------------------------------
SKILL_ALIASES: dict[str, str] = {
    # ── AI / ML / GenAI ─────────────────────────────────────────────────────
    "rag": "retrieval augmented generation",
    "retrieval-augmented generation": "retrieval augmented generation",
    "retrieval augmented generation (rag)": "retrieval augmented generation",
    "llm": "large language model",
    "llms": "large language model",
    "large language models": "large language model",
    "large language models (llms)": "large language model",
    "generative ai": "generative ai",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "llm applications": "large language model",
    "llm-based": "large language model",
    "llm based": "large language model",
    "gpt": "large language model",
    "gpt-4": "large language model",
    "gpt4": "large language model",
    "claude": "large language model",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "natural language processing (nlp)": "natural language processing",
    "cv": "computer vision",
    "opencv": "computer vision",
    "computer vision (opencv)": "computer vision",
    # ── Vector DB ────────────────────────────────────────────────────────────
    "vector db": "vector database",
    "vector dbs": "vector database",
    "milvus": "vector database",
    "vector databases (milvus)": "vector database",
    "vector databases": "vector database",
    "pinecone": "vector database",
    "weaviate": "vector database",
    "chromadb": "vector database",
    "chroma": "vector database",
    "qdrant": "vector database",
    "faiss": "vector database",
    # ── Web Frameworks ───────────────────────────────────────────────────────
    "fastapi": "fastapi",
    "next.js": "nextjs",
    "nextjs": "nextjs",
    "react / next.js": "react",
    "react/next.js": "react",
    "react.js": "react",
    "nodejs": "nodejs",
    "node.js": "nodejs",
    "node js": "nodejs",
    "express.js": "express",
    "expressjs": "express",
    "vue.js": "vue",
    "vuejs": "vue",
    "angularjs": "angular",
    "angular.js": "angular",
    "spring boot": "spring boot",
    "springboot": "spring boot",
    # ── Cloud ────────────────────────────────────────────────────────────────
    "amazon web services": "aws",
    "ec2": "aws",
    "s3": "aws",
    "lambda": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    # ── APIs ─────────────────────────────────────────────────────────────────
    "rest apis": "rest api",
    "rest api": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest api development": "rest api",
    "rest api design": "rest api",
    "api": "rest api",
    "apis": "rest api",
    "web api": "rest api",
    "web apis": "rest api",
    # ── DevOps / Infra ───────────────────────────────────────────────────────
    "k8s": "kubernetes",
    "ci/cd": "ci cd",
    "ci cd": "ci cd",
    "devops": "devops",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "containerization": "docker",
    # ── Databases ────────────────────────────────────────────────────────────
    "mongodb": "mongodb",
    "mongo db": "mongodb",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "mysql": "mysql",
    "redis": "redis",
    "graphql": "graphql",
    "grpc": "grpc",
    # ── ML Libraries ─────────────────────────────────────────────────────────
    "scikit-learn": "scikit learn",
    "sklearn": "scikit learn",
    "huggingface": "huggingface",
    "hugging face": "huggingface",
    "langchain": "langchain",
    "llamaindex": "llamaindex",
    "llama index": "llamaindex",
    "llama-index": "llamaindex",
    "spark": "apache spark",
    "apache spark": "apache spark",
    "hadoop": "hadoop",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "keras": "keras",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
    # ── Visualization ────────────────────────────────────────────────────────
    "tableau": "tableau",
    "power bi": "power bi",
    "powerbi": "power bi",
    # ── ERP / D365 ───────────────────────────────────────────────────────────
    "gl": "general ledger",
    "general ledger (gl)": "general ledger",
    "ap": "accounts payable",
    "accounts payable (ap)": "accounts payable",
    "ar": "accounts receivable",
    "accounts receivable (ar)": "accounts receivable",
    "p2p": "procure to pay",
    "procure-to-pay (p2p)": "procure to pay",
    "procure-to-pay": "procure to pay",
    "procure to pay": "procure to pay",
    "d365 f&o": "dynamics 365 finance operations",
    "d365 fo": "dynamics 365 finance operations",
    "dynamics 365 f&o": "dynamics 365 finance operations",
    "dynamics 365 finance & operations": "dynamics 365 finance operations",
    "dynamics 365 finance and operations": "dynamics 365 finance operations",
    "microsoft dynamics 365 finance & operations": "dynamics 365 finance operations",
    "microsoft dynamics 365 finance and operations": "dynamics 365 finance operations",
    "microsoft dynamics 365 finance & operations (d365 f&o)": "dynamics 365 finance operations",
    "dmf": "data management framework",
    "dixf": "data management framework",
    "data management framework (dmf/dixf)": "data management framework",
    "fdd": "functional documentation",
    "frd": "functional documentation",
    "functional documentation (fdd, frd, sdd)": "functional documentation",
    "azure devops": "azure devops",
    "ado": "azure devops",
    "sit": "sit",
    "uat": "uat",
    "erp": "erp",
    # ── Compliance / AML / KYC ───────────────────────────────────────────────
    "aml": "anti money laundering",
    "anti-money laundering": "anti money laundering",
    "anti money laundering (aml)": "anti money laundering",
    "kyc": "know your customer",
    "know your customer (kyc)": "know your customer",
    "know your client": "know your customer",
    "cdd": "customer due diligence",
    "customer due diligence (cdd)": "customer due diligence",
    "edd": "enhanced due diligence",
    "enhanced due diligence (edd)": "enhanced due diligence",
    "enhanced customer due diligence": "enhanced due diligence",
    "sdd": "simplified due diligence",
    "simplified due diligence (sdd)": "simplified due diligence",
    "bsa": "bank secrecy act",
    "bank secrecy act (bsa)": "bank secrecy act",
    "fca": "financial conduct authority",
    "fatf": "financial action task force",
    "sanctions screening": "sanctions screening",
    "ofac": "ofac sanctions",
    "pep": "politically exposed persons",
    "peps": "politically exposed persons",
    "suspicious activity report": "suspicious activity report",
    "sar": "suspicious activity report",
    "suspicious transaction report": "suspicious transaction report",
    "str": "suspicious transaction report",
    "transaction monitoring": "transaction monitoring",
    "tm": "transaction monitoring",
    "name screening": "name screening",
    "adverse media": "adverse media screening",
    "adverse media screening": "adverse media screening",
    "rfm": "risk-based approach",
    "risk based approach": "risk-based approach",
    "rba": "risk-based approach",
    "customer risk assessment": "customer risk assessment",
    "cra": "customer risk assessment",
    "correspondent banking": "correspondent banking",
    "de-risking": "de-risking",
    "financial crime": "financial crime compliance",
    "financial crime compliance": "financial crime compliance",
    "fcc": "financial crime compliance",
    "compliance": "compliance",
    "regulatory compliance": "compliance",
    "bsaaml": "anti money laundering",
    # ── Finance / Accounting ─────────────────────────────────────────────────
    "fp&a": "financial planning and analysis",
    "financial planning & analysis": "financial planning and analysis",
    "financial planning and analysis": "financial planning and analysis",
    "gaap": "gaap",
    "ifrs": "ifrs",
    "cpa": "cpa",
    "cfa": "cfa",
    "frm": "frm",
    "acca": "acca",
    "cams": "cams",
    "cfcs": "cfcs",
    "cash flow": "cash flow management",
    "budgeting": "budgeting and forecasting",
    "forecasting": "budgeting and forecasting",
    "financial modeling": "financial modeling",
    "financial modelling": "financial modeling",
    "variance analysis": "variance analysis",
    "cost analysis": "cost analysis",
    "management reporting": "management reporting",
    "consolidation": "financial consolidation",
    "financial consolidation": "financial consolidation",
    # ── Banking / Payments ───────────────────────────────────────────────────
    "swift": "swift payments",
    "core banking": "core banking",
    "neft": "neft",
    "rtgs": "rtgs",
    "imps": "imps",
    "upi": "upi",
    "sepa": "sepa",
    "wire transfer": "wire transfer",
    # ── Testing ──────────────────────────────────────────────────────────────
    "selenium": "selenium",
    "junit": "junit",
    "pytest": "pytest",
    "jest": "jest",
    # ── Project Management ───────────────────────────────────────────────────
    "jira": "jira",
    "agile": "agile",
    "scrum": "scrum",
    "kanban": "kanban",
    # ── Languages ────────────────────────────────────────────────────────────
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "go lang": "go",
    "ruby on rails": "ruby on rails",
    "rails": "ruby on rails",
    ".net": "dotnet",
    "dotnet": "dotnet",
    "c#": "csharp",
    "csharp": "csharp",
    "c++": "cpp",
    "cpp": "cpp",
    # ── Misc ─────────────────────────────────────────────────────────────────
    "microservices": "microservices",
    "micro services": "microservices",
    "python backend api development": "fastapi",
    "computer vision": "computer vision",
    "gcp": "gcp",
}

# ---------------------------------------------------------------------------
# RELATED SKILL GROUPS  — partial credit when candidate has adjacent technology
# ---------------------------------------------------------------------------
RELATED_SKILL_GROUPS: list[list[str]] = [
    # Deep Learning frameworks
    ["pytorch", "tensorflow", "keras", "deep learning"],
    # Frontend
    ["react", "nextjs", "vue", "angular", "frontend"],
    # Python web
    ["fastapi", "flask", "django", "python backend"],
    # Cloud
    ["aws", "azure", "gcp", "cloud"],
    # Vector stores
    ["vector database", "milvus", "pinecone", "weaviate", "chromadb", "faiss", "qdrant"],
    # LLM / RAG orchestration
    ["langchain", "llamaindex", "retrieval augmented generation", "generative ai", "large language model"],
    # Computer Vision
    ["computer vision", "opencv", "image processing", "yolo", "cnn"],
    # Containers
    ["docker", "kubernetes", "containerization", "ci cd", "devops"],
    # Databases
    ["postgresql", "mysql", "mongodb", "redis", "sql"],
    # ERP
    ["dynamics 365 finance operations", "erp", "general ledger", "accounts payable", "accounts receivable"],
    # Node/JS backend
    ["nodejs", "express", "nestjs", "backend javascript"],
    # Java
    ["spring boot", "java", "backend"],
    # Data science
    ["scikit learn", "pandas", "numpy", "data science", "machine learning"],
    # Visualization
    ["tableau", "power bi", "data visualization"],
    # Testing
    ["selenium", "pytest", "junit", "jest", "testing"],
    # AML / KYC / Compliance cluster
    [
        "anti money laundering", "know your customer", "customer due diligence",
        "enhanced due diligence", "transaction monitoring", "sanctions screening",
        "financial crime compliance", "suspicious activity report",
        "name screening", "risk-based approach", "compliance",
    ],
    # Finance cluster
    [
        "financial planning and analysis", "budgeting and forecasting", "financial modeling",
        "variance analysis", "management reporting", "gaap", "ifrs",
    ],
    # Banking payments
    ["swift payments", "core banking", "neft", "rtgs", "imps", "upi", "sepa", "wire transfer"],
]

_SOFT_SKILL_PHRASES = {
    "strong communication",
    "problem-solving skills",
    "problem solving skills",
    "communication and problem-solving skills",
    "strong communication and problem-solving skills",
    "team player",
    "attention to detail",
    "self motivated",
    "self-motivated",
    "fast learner",
    "quick learner",
}


def canonicalize(token: str) -> str:
    """Map token to its canonical form via alias lookup."""
    t = re.sub(r"\s+", " ", token.lower().strip())
    t = t.strip(".,;:")
    if not t:
        return t
    if t in SKILL_ALIASES:
        return SKILL_ALIASES[t]
    # Strip parenthetical for lookup: "computer vision (opencv)" -> try inner
    inner = re.findall(r"\(([^)]+)\)", t)
    for part in inner:
        p = part.strip().lower()
        if p in SKILL_ALIASES:
            return SKILL_ALIASES[p]
    # Try without parenthetical suffix
    base = re.sub(r"\s*\([^)]*\)", "", t).strip()
    if base in SKILL_ALIASES:
        return SKILL_ALIASES[base]
    return t


def decompose_skill_phrase(phrase: str) -> list[str]:
    """
    Split compound JD phrases into matchable tokens.
    'React / Next.js' -> ['react', 'nextjs']
    'Computer vision (OpenCV)' -> ['computer vision', 'opencv']
    'AML/KYC/CDD' -> ['anti money laundering', 'know your customer', 'customer due diligence']
    """
    if not phrase or not phrase.strip():
        return []

    tokens: list[str] = []
    phrase = phrase.strip()

    # Parenthetical abbreviations: (OpenCV), (LLMs), (FDD, FRD, SDD)
    for match in re.finditer(r"\(([^)]+)\)", phrase):
        inner = match.group(1)
        for part in re.split(r"[,/&|]", inner):
            p = part.strip()
            if p:
                tokens.append(canonicalize(p))

    # Slash/pipe separated: React / Next.js, AML/KYC
    base = re.sub(r"\([^)]*\)", "", phrase)
    for part in re.split(r"\s*/\s*|\s*\|\s*", base):
        p = part.strip().strip(".,;")
        if p and len(p) > 1:
            tokens.append(canonicalize(p))

    # Comma-separated outside parens: GL, AP, AR
    for part in _split_commas_outside_parens(base):
        p = part.strip().strip(".,;")
        if p and len(p) > 1:
            tokens.append(canonicalize(p))

    # Full phrase canonical form
    tokens.append(canonicalize(phrase))

    # Deduplicate preserving order
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    return result


def _split_commas_outside_parens(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return parts


# Tech keywords mined from resume/JD body text
TECH_KEYWORD_PATTERN = re.compile(
    r"\b("
    r"Python|Java(?:Script)?|TypeScript|React(?:\.js)?|Next(?:\.js)?|Node(?:\.js)?|"
    r"FastAPI|Flask|Django|AWS|Azure|GCP|Docker|Kubernetes|K8s|"
    r"PostgreSQL|MongoDB|Redis|Milvus|Pinecone|Weaviate|Chroma(?:DB)?|Qdrant|FAISS|"
    r"OpenCV|TensorFlow|PyTorch|LangChain|LlamaIndex|HuggingFace|XGBoost|LightGBM|"
    r"RAG|LLM(?:s)?|GPT|BERT|Transformer(?:s)?|GenAI|"
    r"REST(?:ful)?(?:\s+APIs?)?|GraphQL|gRPC|DevOps|"
    r"CI/CD|Git(?:Hub|Lab)?|Jira|Agile|Scrum|"
    r"Dynamics\s*365|D365|Finance\s*(?:&|and)\s*Operations|"
    r"General\s+Ledger|Accounts\s+Payable|Accounts\s+Receivable|"
    r"Procure[\-\s]to[\-\s]Pay|Data\s+Management\s+Framework|"
    r"AML|KYC|CDD|EDD|BSA|FATF|OFAC|CAMS|"
    r"Transaction\s+Monitoring|Sanctions\s+Screening|"
    r"Anti[\-\s]Money\s+Laundering|Know\s+Your\s+Customer|"
    r"Customer\s+Due\s+Diligence|Enhanced\s+Due\s+Diligence|"
    r"Financial\s+Crime\s+Compliance|Suspicious\s+Activity\s+Report"
    r")\b",
    re.I,
)

_ABBREV_PATTERN = re.compile(
    r"\b(GL|AP|AR|P2P|DMF|DIXF|FDD|FRD|SDD|D365|F&O|UAT|SIT|ERP|ADO|"
    r"RAG|LLM?s?|AML|KYC|CDD|EDD|BSA|SAR|STR|PEP|TM|FCA|FATF|OFAC|"
    r"CAMS|CFCS|FRM|CPA|CFA|ACCA|GAAP|IFRS|FP&A|RBA|CRA|FCC)\b",
    re.I,
)


def mine_tech_keywords(text: str) -> list[str]:
    """Extract known technology tokens from free text."""
    found: list[str] = []
    seen: set[str] = set()

    for match in TECH_KEYWORD_PATTERN.finditer(text):
        token = canonicalize(match.group(0))
        if token and token not in seen:
            seen.add(token)
            found.append(token)

    for match in _ABBREV_PATTERN.finditer(text):
        token = canonicalize(match.group(0))
        if token and token not in seen:
            seen.add(token)
            found.append(token)

    return found


def is_soft_skill_only(phrase: str) -> bool:
    """True if phrase is generic soft skill, not a technical requirement."""
    p = phrase.lower().strip()
    return p in _SOFT_SKILL_PHRASES or (
        len(p.split()) <= 4
        and not mine_tech_keywords(phrase)
        and any(w in p for w in ("communication", "problem solving", "teamwork", "leadership", "interpersonal"))
    )


def find_related_skill(jd_canon: str, resume_canon: str) -> bool:
    """True if resume skill is in the same related group as JD skill."""
    if not jd_canon or not resume_canon:
        return False
    if jd_canon == resume_canon:
        return True
    for group in RELATED_SKILL_GROUPS:
        jd_in = any(g in jd_canon or jd_canon in g for g in group)
        res_in = any(g in resume_canon or resume_canon in g for g in group)
        if jd_in and res_in:
            return True
    return False
