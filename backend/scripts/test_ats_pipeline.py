"""Quick ATS pipeline smoke test."""
import asyncio
import uuid

from app.ats.orchestrator.ats_orchestrator import ats_orchestrator

RESUME = """
John Smith
Software Engineer

Skills
Python, FastAPI, React, Next.js, AWS, Docker, PyTorch, OpenCV, RAG, LLMs

Experience
Senior Software Engineer | Tech Corp | 2020 - Present
- Built REST APIs with FastAPI and deployed on AWS
- Developed computer vision pipelines using OpenCV and PyTorch
- Implemented RAG systems with vector databases

Education
B.Tech Computer Science, IIT Delhi, 2018
Master of Science in Data Science, Stanford University, 2020

Projects
AI Resume Analyzer - Built with FastAPI, React, Milvus
"""

JD = """
Senior AI Engineer

Required Skills
Python, FastAPI, React/Next.js, AWS, Docker, OpenCV, RAG, LLMs

Responsibilities
- Design and build REST APIs
- Develop computer vision and ML pipelines
- Implement retrieval augmented generation systems

Education
Bachelor's degree in Computer Science or related field

Preferred Skills
PyTorch, Kubernetes, Milvus
"""


async def main():
    result = await ats_orchestrator.run(
        resume_text=RESUME,
        jd_text=JD,
        user_id=uuid.uuid4(),
        resume_id=uuid.uuid4(),
        db=None,  # type: ignore
    )
    print("ATS Score:", result["ats_score"])
    print("Match Score:", result["match_score"])
    print("Confidence:", result.get("confidence_score"))
    print("Score Breakdown:", result.get("score_breakdown"))
    print("Education Score:", result["education_score"])
    print("Education Detail:", result["detailed_scores"]["education_match_score"])
    print("Project Score:", result["project_score"])
    print("Score Weights:", result.get("score_weights", {}))
    print("Matched Skills:", result["matched_skills"][:8])
    print("Missing Skills:", result["missing_skills"])


if __name__ == "__main__":
    asyncio.run(main())
