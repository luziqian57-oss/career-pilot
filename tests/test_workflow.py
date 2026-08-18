import pytest

from career_pilot.agents.workflow import career_workflow


@pytest.mark.asyncio
async def test_career_workflow() -> None:
    result = await career_workflow.ainvoke(
        {
            "resume_text": "Alex Chen builds APIs with Python, FastAPI, Redis and Docker.",
            "job_description": "Looking for Python, FastAPI, PostgreSQL and Docker experience.",
        }
    )

    assert result["parsed_resume"].name == (
        "Alex Chen builds APIs with Python, FastAPI, Redis and Docker."
    )
    assert result["match_analysis"].score == 75
    assert result["match_analysis"].missing_skills == ["postgresql"]
