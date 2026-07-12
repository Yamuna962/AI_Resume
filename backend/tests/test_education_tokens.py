import pytest

from app.ats.normalization.education_tokens import (
    canonical_degree_level,
    canonical_field,
    education_requirements_match,
    parse_education_line,
)


def test_generic_bachelors_requirement_accepts_bcom() -> None:
    jd_requirement = "Bachelor's Degree or higher in relevant field"
    resume_entry = parse_education_line("B.Com, Osmania University 2019")

    credit, reason = education_requirements_match(jd_requirement, [resume_entry])

    assert canonical_degree_level(jd_requirement) == "bachelors"
    assert canonical_field(jd_requirement) is None
    assert credit == pytest.approx(1.0)
    assert reason
