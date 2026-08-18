import re

from career_pilot.schemas import ParsedResume

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")

KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "fastapi",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "langchain",
    "langgraph",
    "pytorch",
    "tensorflow",
    "machine learning",
    "rag",
}


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    return sorted(skill for skill in KNOWN_SKILLS if re.search(rf"\b{re.escape(skill)}\b", lowered))


def parse_resume_text(text: str) -> ParsedResume:
    """Provide a fast deterministic baseline; an LLM parser can replace this service later."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    name = lines[0][:100] if lines and not EMAIL_RE.search(lines[0]) else None
    skills = extract_skills(text)
    summary = f"Candidate profile with {len(skills)} recognized technical skills."

    return ParsedResume(
        name=name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        skills=skills,
        summary=summary,
    )
