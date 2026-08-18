from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from career_pilot import __version__
from career_pilot.api.routes import router
from career_pilot.config import get_settings
from career_pilot.infrastructure.database import close_database
from career_pilot.services.document_extractor import DocumentExtractionError
from career_pilot.services.llm.factory import create_llm_provider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.llm = create_llm_provider(get_settings())
    yield
    await app.state.llm.close()
    await close_database()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="API for resume parsing and job matching workflows.",
        lifespan=lifespan,
    )
    app.include_router(router, prefix=settings.api_v1_prefix)

    @app.exception_handler(DocumentExtractionError)
    async def document_error_handler(
        request: Request, exc: DocumentExtractionError
    ) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    return app


app = create_app()
