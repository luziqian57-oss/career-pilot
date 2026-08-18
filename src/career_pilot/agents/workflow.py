from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from career_pilot.schemas import MatchAnalysis, ParsedResume
from career_pilot.services.job_matcher import analyze_job_match
from career_pilot.services.llm.mock import MockLLMProvider
from career_pilot.services.resume_parser import parse_resume_text


class CareerState(TypedDict):
    resume_text: str
    job_description: str
    parsed_resume: NotRequired[ParsedResume]
    match_analysis: NotRequired[MatchAnalysis]


async def parse_resume_node(state: CareerState) -> dict[str, ParsedResume]:
    return {"parsed_resume": parse_resume_text(state["resume_text"])}


async def match_job_node(state: CareerState) -> dict[str, MatchAnalysis]:
    # The compiled skeleton stays deterministic. API services can inject a real provider.
    analysis = await analyze_job_match(
        state["parsed_resume"], state["job_description"], MockLLMProvider()
    )
    return {"match_analysis": analysis}


builder = StateGraph(CareerState)
builder.add_node("parse_resume", parse_resume_node)
builder.add_node("match_job", match_job_node)
builder.add_edge(START, "parse_resume")
builder.add_edge("parse_resume", "match_job")
builder.add_edge("match_job", END)
career_workflow = builder.compile()
