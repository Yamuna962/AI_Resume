"""Deterministic ATS formatting analyzer."""
from __future__ import annotations

import re

from app.ats.domain.interfaces import IFormattingAnalyzer
from app.ats.domain.schemas import FormattingResult, ParsedResume

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.\w+")
_PHONE = re.compile(r"\+?\d[\d\s\-().]{7,}\d")
_BULLET = re.compile(r"^[\u2022\-\*\u2023]", re.M)
_TABLE_HINT = re.compile(r"\|{2,}|\t{3,}")
_IMAGE_HINT = re.compile(r"\[image|\(image|figure\s+\d", re.I)


class FormattingAnalyzer(IFormattingAnalyzer):
    """Checks ATS-friendly formatting signals — fully deterministic."""

    def analyze(self, resume: ParsedResume) -> FormattingResult:
        text = resume.raw_text
        issues: list[str] = []
        recommendations: list[str] = []
        checks: list[tuple[str, bool, str]] = [
            ("Extractable PDF text", len(text.strip()) > 100, "Resume text could not be extracted"),
            ("Contact email", bool(_EMAIL.search(text)), "Add a professional email address"),
            ("Contact phone", bool(_PHONE.search(text)), "Add a phone number"),
            ("Professional summary", bool(resume.summary.strip()), "Add a Professional Summary section"),
            ("Experience section", bool(resume.experience), "Add an Experience section"),
            ("Skills section", bool(resume.skills), "Add a Skills section"),
            ("Education section", bool(resume.education), "Add an Education section"),
            ("Bullet points", bool(_BULLET.search(text)), "Use bullet points for achievements"),
            ("No tables", not bool(_TABLE_HINT.search(text)), "Avoid tables — ATS cannot parse them"),
            ("No images", not bool(_IMAGE_HINT.search(text)), "Avoid images/icons in the resume"),
        ]

        if resume.projects:
            checks.append(("Projects section", True, ""))
        if resume.certifications:
            checks.append(("Certifications section", True, ""))

        passed = 0
        for name, ok, rec in checks:
            if ok:
                passed += 1
            else:
                issues.append(name)
                if rec:
                    recommendations.append(rec)

        total = len(checks)
        formatting_score = round(passed / total * 100, 2) if total else 0.0

        # Don't recommend formatting improvements when formatting is already near-perfect (>= 90%)
        if formatting_score >= 90.0:
            recommendations = []

        return FormattingResult(
            formatting_score=formatting_score,
            issues=issues,
            recommendations=recommendations,
        )


formatting_analyzer = FormattingAnalyzer()
