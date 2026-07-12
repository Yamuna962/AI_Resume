"""
Multi-engine PDF text extractor for resumes.

Runs several extraction strategies and picks the highest-quality result:
  1. pymupdf4llm  — structured Markdown (best for section headers)
  2. pdfplumber   — layout-aware character positioning
  3. PyMuPDF      — column-aware word reconstruction
  4. OCR          — pytesseract fallback for scanned/image PDFs
"""
from __future__ import annotations

import io
import os
import re
import shutil
from dataclasses import dataclass
from typing import Any

import fitz  # PyMuPDF
from loguru import logger

from app.core.config import settings

_MIN_TEXT_LENGTH = 80

_SECTION_KEYWORDS = re.compile(
    r"(?i)\b(experience|education|skills|projects|certifications|summary|"
    r"employment|qualifications|objective|profile)\b"
)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.\w+")
_PHONE = re.compile(r"\+?\d[\d\s\-().]{7,}\d")


@dataclass
class ExtractionCandidate:
    text: str
    method: str
    quality_score: float


@dataclass
class PDFExtractionResult:
    text: str
    page_count: int
    char_count: int
    is_likely_scanned: bool
    extraction_method: str
    quality_score: float


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    result = extract_text_from_pdf_detailed(file_bytes)
    if result.char_count < _MIN_TEXT_LENGTH:
        raise ValueError(
            "Could not extract enough readable text from this PDF. "
            "If this is a scanned resume, install Tesseract OCR. "
            "Otherwise export a text-based PDF from Word or Google Docs."
        )
    return result.text


def extract_text_from_pdf_detailed(file_bytes: bytes) -> PDFExtractionResult:
    """Run all engines, return the best extraction by quality score."""
    try:
        doc = getattr(fitz, "open")(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Invalid or corrupted PDF: {exc}") from exc

    page_count = len(doc)
    candidates: list[ExtractionCandidate] = []

    # Engine 1: pymupdf4llm → Markdown
    candidates.append(_try_pymupdf4llm(doc))

    # Engine 2: pdfplumber layout extraction
    candidates.append(_try_pdfplumber(file_bytes))

    # Engine 3: PyMuPDF column-aware
    candidates.append(_try_pymupdf_layout(doc))

    # Engine 4: OCR for scanned/image PDFs
    best_so_far = max((c.quality_score for c in candidates if c.text), default=0)
    total_chars = max((len(c.text) for c in candidates if c.text), default=0)
    if best_so_far < 50 or total_chars < 200:
        candidates.append(_try_ocr(doc))

    doc.close()

    valid = [c for c in candidates if c.text and c.text.strip()]
    if not valid:
        return PDFExtractionResult(
            text="",
            page_count=page_count,
            char_count=0,
            is_likely_scanned=True,
            extraction_method="none",
            quality_score=0.0,
        )

    winner = max(valid, key=lambda c: c.quality_score)
    cleaned = _post_process(winner.text)

    logger.info(
        f"PDF extraction winner: method={winner.method} "
        f"quality={winner.quality_score:.1f} chars={len(cleaned)} pages={page_count} "
        f"(candidates: {[(c.method, round(c.quality_score, 1)) for c in valid]})"
    )

    return PDFExtractionResult(
        text=cleaned,
        page_count=page_count,
        char_count=len(cleaned),
        is_likely_scanned=winner.method == "ocr" or winner.quality_score < 30,
        extraction_method=winner.method,
        quality_score=winner.quality_score,
    )


# ---------------------------------------------------------------------------
# Quality scoring
# ---------------------------------------------------------------------------

def _score_text(text: str, method: str) -> float:
    """Score extraction quality — higher is better. Deterministic."""
    if not text or not text.strip():
        return 0.0

    score = 0.0
    length = len(text.strip())

    # Length (cap at 30 pts)
    score += min(length / 600, 1.0) * 30

    # Section headers detected (cap at 25 pts)
    headers = len(_SECTION_KEYWORDS.findall(text))
    score += min(headers * 5, 25)

    # Contact info (15 pts)
    if _EMAIL.search(text):
        score += 8
    if _PHONE.search(text):
        score += 7

    # Alphanumeric ratio (20 pts) — penalize garbled output
    alnum = sum(c.isalnum() or c.isspace() for c in text) / max(len(text), 1)
    score += alnum * 20

    # Line structure (10 pts) — resumes should have multiple lines
    lines = [ln for ln in text.splitlines() if ln.strip()]
    score += min(len(lines) / 20, 1.0) * 10

    # Method bonus — prefer structured extractors
    method_bonus = {
        "pymupdf4llm": 8,
        "pdfplumber": 6,
        "pymupdf-layout": 4,
        "ocr": 0,
    }
    score += method_bonus.get(method, 0)

    return round(min(score, 100.0), 2)


# ---------------------------------------------------------------------------
# Engine 1: pymupdf4llm
# ---------------------------------------------------------------------------

def _try_pymupdf4llm(doc: Any) -> ExtractionCandidate:
    try:
        import pymupdf4llm
        md = pymupdf4llm.to_markdown(doc, page_chunks=False)
        text = md if isinstance(md, str) else str(md)
        return ExtractionCandidate(text=text, method="pymupdf4llm", quality_score=_score_text(text, "pymupdf4llm"))
    except ImportError:
        logger.debug("pymupdf4llm not installed")
        return ExtractionCandidate(text="", method="pymupdf4llm", quality_score=0)
    except Exception as exc:
        logger.warning(f"pymupdf4llm extraction failed: {exc}")
        return ExtractionCandidate(text="", method="pymupdf4llm", quality_score=0)


# ---------------------------------------------------------------------------
# Engine 2: pdfplumber
# ---------------------------------------------------------------------------

def _try_pdfplumber(file_bytes: bytes) -> ExtractionCandidate:
    try:
        import pdfplumber
        parts: list[str] = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                # layout=True preserves visual reading order
                page_text = page.extract_text(
                    layout=True,
                    x_tolerance=2,
                    y_tolerance=3,
                    keep_blank_chars=False,
                )
                if page_text and page_text.strip():
                    parts.append(page_text.strip())
                else:
                    # Word-level fallback for pages with no flow text
                    words = page.extract_words(x_tolerance=2, y_tolerance=3)
                    if words:
                        parts.append(_pdfplumber_words_to_text(words))
        text = "\n\n".join(parts)
        return ExtractionCandidate(text=text, method="pdfplumber", quality_score=_score_text(text, "pdfplumber"))
    except ImportError:
        logger.debug("pdfplumber not installed")
        return ExtractionCandidate(text="", method="pdfplumber", quality_score=0)
    except Exception as exc:
        logger.warning(f"pdfplumber extraction failed: {exc}")
        return ExtractionCandidate(text="", method="pdfplumber", quality_score=0)


def _pdfplumber_words_to_text(words: list[dict]) -> str:
    """Reconstruct lines from pdfplumber word dicts sorted by position."""
    line_map: dict[int, list[tuple[float, str]]] = {}
    for w in words:
        word = w.get("text", "").strip()
        if not word:
            continue
        top = int(round(w.get("top", 0) / 3) * 3)
        line_map.setdefault(top, []).append((w.get("x0", 0), word))
    lines = []
    for top in sorted(line_map.keys()):
        row = sorted(line_map[top], key=lambda t: t[0])
        lines.append(" ".join(tok for _, tok in row))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Engine 3: PyMuPDF column-aware layout
# ---------------------------------------------------------------------------

def _try_pymupdf_layout(doc: Any) -> ExtractionCandidate:
    try:
        parts: list[str] = []
        for page in doc:
            text = _extract_page_layout(page)
            if text.strip():
                parts.append(text)
        text = "\n\n".join(parts)
        return ExtractionCandidate(text=text, method="pymupdf-layout", quality_score=_score_text(text, "pymupdf-layout"))
    except Exception as exc:
        logger.warning(f"PyMuPDF layout extraction failed: {exc}")
        return ExtractionCandidate(text="", method="pymupdf-layout", quality_score=0)


def _extract_page_layout(page: Any) -> str:
    words = page.get_text("words", sort=True)
    if not words:
        return page.get_text("text", sort=True) or ""

    page_width = page.rect.width
    mid_x = page_width * 0.48
    left = [w for w in words if w[0] < mid_x]
    right = [w for w in words if w[0] >= mid_x]

    if left and right and len(right) > 5:
        return _words_to_lines(left) + "\n" + _words_to_lines(right)
    return _words_to_lines(words)


def _words_to_lines(words: list) -> str:
    line_map: dict[int, list[tuple[float, str]]] = {}
    for w in words:
        x0, y0, _, _, word, *_ = w
        if not str(word).strip():
            continue
        y_key = int(round(y0 / 3) * 3)
        line_map.setdefault(y_key, []).append((x0, str(word)))
    return "\n".join(
        " ".join(tok for _, tok in sorted(line_map[y], key=lambda t: t[0]))
        for y in sorted(line_map.keys())
    )


# ---------------------------------------------------------------------------
# Engine 4: OCR (scanned PDFs)
# ---------------------------------------------------------------------------

def _configure_tesseract() -> bool:
    """Point pytesseract at the installed Tesseract binary."""
    try:
        import pytesseract
    except ImportError:
        return False

    candidates = [
        settings.TESSERACT_CMD,
        os.environ.get("TESSERACT_CMD", ""),
        shutil.which("tesseract") or "",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.debug(f"Tesseract configured: {path}")
            return True

    logger.warning(
        "Tesseract executable not found. Install Tesseract or set TESSERACT_CMD in your environment."
    )
    return False


def _try_ocr(doc: Any) -> ExtractionCandidate:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        logger.debug("pytesseract/Pillow not installed — OCR unavailable")
        return ExtractionCandidate(text="", method="ocr", quality_score=0)

    if not _configure_tesseract():
        return ExtractionCandidate(text="", method="ocr", quality_score=0)

    parts: list[str] = []
    for page_num, page in enumerate(doc):
        try:
            pix = page.get_pixmap(dpi=300, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            page_text = pytesseract.image_to_string(
                img,
                config="--psm 6 -c preserve_interword_spaces=1",
            )
            if page_text.strip():
                parts.append(page_text.strip())
                logger.debug(f"OCR page {page_num + 1}: {len(page_text)} chars")
        except Exception as exc:
            logger.warning(f"OCR failed on page {page_num + 1}: {exc}")

    text = "\n\n".join(parts)
    if text.strip():
        logger.info(f"OCR extracted {len(text)} chars from {len(doc)} page(s)")
    return ExtractionCandidate(text=text, method="ocr", quality_score=_score_text(text, "ocr"))


# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------

def _post_process(text: str) -> str:
    if not text:
        return ""

    # Strip markdown heading markers from pymupdf4llm output but keep structure
    text = re.sub(r"^#{1,4}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)

    # Fix hyphenation across lines
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize unicode
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2022", "•").replace("\uf0b7", "•")

    lines: list[str] = []
    prev = None
    for line in text.splitlines():
        cleaned = re.sub(r"[ \t]+", " ", line).strip()
        if cleaned and cleaned != prev:
            lines.append(cleaned)
        prev = cleaned

    return "\n".join(lines)
