from career_pilot.schemas import MatchAnalysis, ParsedResume
from career_pilot.services.llm.base import LLMProvider
from career_pilot.services.llm.mock import MockLLMProvider
from career_pilot.services.resume_parser import extract_skills


async def analyze_job_match(
    resume: ParsedResume, job_description: str, llm: LLMProvider
) -> MatchAnalysis:
    """Analyze fit with an offline baseline or a provider-backed structured response."""
    if not isinstance(llm, MockLLMProvider):
        return await llm.generate_structured(
            system_prompt=(
                "You are a fair recruiting assistant. Compare evidence in the resume with the job "
                "description. Do not infer protected attributes or invent experience. "
                "Return a concise structured assessment."
            ),
            user_prompt=(
                f"Resume:\n{resume.model_dump_json()}\n\nJob description:\n{job_description}"
            ),
            response_model=MatchAnalysis,
        )

    required = set(extract_skills(job_description))
    candidate = set(resume.skills)
    matched = sorted(required & candidate)
    missing = sorted(required - candidate)
    score = round(100 * len(matched) / len(required)) if required else 50
    strengths = [f"Demonstrated {skill}" for skill in matched[:5]]
    recommendations = [f"Add evidence of {skill} experience" for skill in missing[:5]]
    if not strengths:
        strengths = ["Resume is available for a broader experience review"]
    if not recommendations:
        recommendations = ["Quantify achievements relevant to this role"]

    return MatchAnalysis(
        score=score,
        matched_skills=matched,
        missing_skills=missing,
        strengths=strengths,
        recommendations=recommendations,
        rationale=(
            f"Deterministic baseline found {len(matched)} of {len(required)} recognized skills "
            "from the job description in the resume."
        ),
    )
