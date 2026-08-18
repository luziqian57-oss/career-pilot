from pydantic import BaseModel, Field


class Experience(BaseModel):
    title: str
    organization: str | None = None
    duration: str | None = None


class ParsedResume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    summary: str


class ResumeParseRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50_000, examples=["Jane Doe\nPython, FastAPI..."])


class MatchAnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=20, max_length=50_000)
    job_description: str = Field(min_length=20, max_length=50_000)


class MatchAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    recommendations: list[str]
    rationale: str


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str


class ResumeUploadResponse(BaseModel):
    filename: str
    content_type: str
    extracted_characters: int
    parsed_resume: ParsedResume


class MatchUploadResponse(BaseModel):
    filename: str
    extracted_characters: int
    analysis: MatchAnalysis
