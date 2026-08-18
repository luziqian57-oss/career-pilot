import asyncio
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from career_pilot.config import Settings

PDF_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
DOCX_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}


class DocumentExtractionError(Exception):
    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class ExtractedDocument:
    filename: str
    content_type: str
    text: str


async def extract_uploaded_document(upload: UploadFile, settings: Settings) -> ExtractedDocument:
    filename = Path((upload.filename or "").replace("\\", "/")).name
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise DocumentExtractionError(
            "Only .pdf and .docx resume files are supported. Legacy .doc files must be "
            "saved as .docx first.",
            status_code=415,
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await upload.read(max_bytes + 1)
    await upload.close()
    if not content:
        raise DocumentExtractionError("The uploaded file is empty.")
    if len(content) > max_bytes:
        raise DocumentExtractionError(
            f"The uploaded file exceeds the {settings.max_upload_size_mb} MB limit.",
            status_code=413,
        )

    content_type = (upload.content_type or "application/octet-stream").lower()
    if extension == ".pdf":
        _validate_content_type(content_type, PDF_CONTENT_TYPES)
        if not content.startswith(b"%PDF-"):
            raise DocumentExtractionError("The file does not contain a valid PDF signature.")
        text = await asyncio.to_thread(_extract_pdf_text, content)
    else:
        _validate_content_type(content_type, DOCX_CONTENT_TYPES)
        if not content.startswith(b"PK"):
            raise DocumentExtractionError("The file does not contain a valid DOCX signature.")
        _validate_docx_archive(content, max_bytes * 4)
        text = await asyncio.to_thread(_extract_docx_text, content)

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        raise DocumentExtractionError(
            "No readable text was found. The document may be scanned or image-only; OCR is not "
            "included in v0.2."
        )
    if len(text) > settings.max_extracted_text_characters:
        raise DocumentExtractionError(
            "The extracted document text exceeds the configured character limit.", status_code=413
        )

    return ExtractedDocument(filename=filename, content_type=content_type, text=text)


def _validate_content_type(content_type: str, allowed: set[str]) -> None:
    if content_type not in allowed:
        raise DocumentExtractionError(f"Unsupported content type: {content_type}.", status_code=415)


def _extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise DocumentExtractionError("Password-protected PDF files are not supported.")
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except DocumentExtractionError:
        raise
    except (PdfReadError, ValueError, OSError) as exc:
        raise DocumentExtractionError("The PDF could not be read safely.") from exc
    except Exception as exc:
        raise DocumentExtractionError("The PDF contains unsupported or malformed data.") from exc


def _validate_docx_archive(content: bytes, max_expanded_bytes: int) -> None:
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            entries = archive.infolist()
            if len(entries) > 2_000:
                raise DocumentExtractionError("The DOCX archive contains too many entries.")
            if sum(entry.file_size for entry in entries) > max_expanded_bytes:
                raise DocumentExtractionError(
                    "The expanded DOCX file is too large.", status_code=413
                )
            if "word/document.xml" not in {entry.filename for entry in entries}:
                raise DocumentExtractionError("The archive is not a valid DOCX document.")
    except zipfile.BadZipFile as exc:
        raise DocumentExtractionError("The DOCX archive could not be read.") from exc


def _extract_docx_text(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
        blocks = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        for table in document.tables:
            for row in table.rows:
                values = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if values:
                    blocks.append(" | ".join(values))
        return "\n".join(blocks)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        raise DocumentExtractionError("The DOCX document could not be read safely.") from exc
    except Exception as exc:
        raise DocumentExtractionError(
            "The DOCX document contains unsupported or malformed data."
        ) from exc
