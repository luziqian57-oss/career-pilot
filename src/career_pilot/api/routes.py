from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from career_pilot import __version__
from career_pilot.api.dependencies import get_llm
from career_pilot.config import get_settings
from career_pilot.schemas import (
    HealthResponse,
    MatchAnalysis,
    MatchAnalysisRequest,
    MatchUploadResponse,
    ParsedResume,
    ResumeParseRequest,
    ResumeUploadResponse,
)
from career_pilot.services.document_extractor import extract_uploaded_document
from career_pilot.services.job_matcher import analyze_job_match
from career_pilot.services.llm.base import LLMProvider
from career_pilot.services.resume_parser import parse_resume_text

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version=__version__, llm_provider=settings.llm_provider)


@router.post("/resumes/parse", response_model=ParsedResume, tags=["resumes"])
async def parse_resume(payload: ResumeParseRequest) -> ParsedResume:
    return parse_resume_text(payload.text)


@router.post("/resumes/upload", response_model=ResumeUploadResponse, tags=["resumes"])
async def upload_resume(file: Annotated[UploadFile, File(...)]) -> ResumeUploadResponse:
    document = await extract_uploaded_document(file, get_settings())
    return ResumeUploadResponse(
        filename=document.filename,
        content_type=document.content_type,
        extracted_characters=len(document.text),
        parsed_resume=parse_resume_text(document.text),
    )


@router.post("/matches/analyze", response_model=MatchAnalysis, tags=["matching"])
async def analyze_match(
    payload: MatchAnalysisRequest, llm: Annotated[LLMProvider, Depends(get_llm)]
) -> MatchAnalysis:
    resume = parse_resume_text(payload.resume_text)
    return await analyze_job_match(resume, payload.job_description, llm)


@router.post("/matches/analyze-upload", response_model=MatchUploadResponse, tags=["matching"])
async def analyze_uploaded_resume(
    file: Annotated[UploadFile, File(...)],
    job_description: Annotated[str, Form(min_length=20, max_length=50_000)],
    llm: Annotated[LLMProvider, Depends(get_llm)],
) -> MatchUploadResponse:
    document = await extract_uploaded_document(file, get_settings())
    resume = parse_resume_text(document.text)
    analysis = await analyze_job_match(resume, job_description, llm)
    return MatchUploadResponse(
        filename=document.filename,
        extracted_characters=len(document.text),
        analysis=analysis,
    )
