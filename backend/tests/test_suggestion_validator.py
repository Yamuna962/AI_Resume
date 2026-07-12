from app.ats.domain.schemas import LLMExplanation, ParsedExperience, ParsedResume, PrioritizedRecommendations
from app.ats.llm.suggestion_validator import validate_explanation


def test_validator_removes_existing_skill_and_formatting_recommendations() -> None:
    resume = ParsedResume(
        skills=["Microsoft Excel", "Transaction Monitoring"],
        experience=[
            ParsedExperience(
                title="AML Analyst",
                bullets=["Used Microsoft Excel for reporting and transaction review."],
            )
        ],
    )
    explanation = LLMExplanation(
        recommendations=[
            "Add Microsoft Excel to the skills section.",
            "Quantify achievements with metrics.",
            "Improve the resume formatting to make it ATS-friendly.",
        ],
        recommendations_prioritized=PrioritizedRecommendations(
            high_priority=["Quantify achievements with metrics."],
            medium_priority=[
                "Quantify achievements with metrics.",
                "Improve the resume formatting to make it ATS-friendly.",
            ],
            low_priority=[],
        ),
    )

    validated = validate_explanation(resume, explanation, formatting_score=100.0)

    assert validated.recommendations == ["Quantify achievements with metrics."]
    assert validated.recommendations_prioritized.high_priority == [
        "Quantify achievements with metrics."
    ]
    assert validated.recommendations_prioritized.medium_priority == []
    assert validated.recommendations_prioritized.low_priority == []


def test_validator_removes_truncated_prefix_duplicates() -> None:
    resume = ParsedResume()
    short = "Incorporate more metrics or quantifiable achievements into the resume to improve"
    long = (
        "Incorporate more metrics or quantifiable achievements into the resume "
        "to improve the business impact score."
    )
    explanation = LLMExplanation(recommendations=[short, long])

    validated = validate_explanation(resume, explanation)

    assert validated.recommendations == [long]
