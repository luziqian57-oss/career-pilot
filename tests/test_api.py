from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from career_pilot.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.2.0"


def test_parse_resume() -> None:
    resume = """Jane Doe
jane@example.com | +1 555 123 4567
Backend Engineer using Python, FastAPI, PostgreSQL, Redis and Docker.
"""
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/parse", json={"text": resume})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Jane Doe"
    assert body["email"] == "jane@example.com"
    assert {"python", "fastapi", "postgresql", "redis", "docker"} <= set(body["skills"])


def test_analyze_match_with_offline_provider() -> None:
    payload = {
        "resume_text": "Jane Doe is a backend engineer skilled in Python, FastAPI and Docker.",
        "job_description": "We need an engineer with Python, FastAPI, PostgreSQL and AWS skills.",
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/matches/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 50
    assert body["matched_skills"] == ["fastapi", "python"]
    assert body["missing_skills"] == ["aws", "postgresql"]


def test_rejects_too_short_resume() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/parse", json={"text": "too short"})

    assert response.status_code == 422


def make_docx_resume() -> bytes:
    stream = BytesIO()
    document = Document()
    document.add_paragraph("Taylor Smith")
    document.add_paragraph("taylor@example.com")
    document.add_paragraph("Backend engineer using Python, FastAPI, Redis and Docker.")
    document.save(stream)
    return stream.getvalue()


def make_pdf_resume(text: str = "Morgan Lee - Python FastAPI PostgreSQL Docker") -> bytes:
    stream = BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.drawString(72, 750, text)
    pdf.save()
    return stream.getvalue()


def test_upload_docx_resume() -> None:
    files = {
        "file": (
            "resume.docx",
            make_docx_resume(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/upload", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "resume.docx"
    assert body["parsed_resume"]["name"] == "Taylor Smith"
    assert {"python", "fastapi", "redis", "docker"} <= set(body["parsed_resume"]["skills"])


def test_upload_pdf_resume() -> None:
    files = {"file": ("resume.pdf", make_pdf_resume(), "application/pdf")}
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/upload", files=files)

    assert response.status_code == 200
    assert response.json()["parsed_resume"]["skills"] == [
        "docker",
        "fastapi",
        "postgresql",
        "python",
    ]


def test_analyze_uploaded_resume() -> None:
    files = {
        "file": (
            "resume.docx",
            make_docx_resume(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    data = {"job_description": "We need Python, FastAPI, PostgreSQL and AWS experience."}
    with TestClient(app) as client:
        response = client.post("/api/v1/matches/analyze-upload", files=files, data=data)

    assert response.status_code == 200
    assert response.json()["analysis"]["score"] == 50
    assert response.json()["analysis"]["missing_skills"] == ["aws", "postgresql"]


def test_rejects_legacy_word_file() -> None:
    files = {"file": ("resume.doc", b"legacy word content", "application/msword")}
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/upload", files=files)

    assert response.status_code == 415
    assert "saved as .docx" in response.json()["detail"]


def test_rejects_image_only_pdf() -> None:
    stream = BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.showPage()
    pdf.save()
    files = {"file": ("scan.pdf", stream.getvalue(), "application/pdf")}
    with TestClient(app) as client:
        response = client.post("/api/v1/resumes/upload", files=files)

    assert response.status_code == 422
    assert "OCR" in response.json()["detail"]
