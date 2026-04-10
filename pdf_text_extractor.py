from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


PathLike = Union[str, Path]


class PDFExtractionError(Exception):
    """Raised when PDF text extraction cannot be completed."""


@dataclass
class PDFPageText:
    page_number: int
    text: str


def _get_pdf_reader(pdf_path: PathLike):
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path}")

    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except Exception as exc:
            raise PDFExtractionError(
                "No supported PDF library found. Install 'pypdf' (recommended) "
                "or 'PyPDF2' to enable extraction."
            ) from exc

    try:
        return PdfReader(str(path))
    except Exception as exc:
        raise PDFExtractionError(f"Failed to read PDF: {path}") from exc


def extract_text_by_page(
    pdf_path: PathLike,
    *,
    strip: bool = True,
    skip_empty: bool = False,
) -> List[PDFPageText]:
    """
    Extract text from each page of a PDF.

    Returns a list of PDFPageText objects with 1-based page numbers.
    """
    reader = _get_pdf_reader(pdf_path)
    pages: List[PDFPageText] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if strip:
            text = text.strip()
        if skip_empty and not text:
            continue
        pages.append(PDFPageText(page_number=index, text=text))

    return pages


def extract_text(
    pdf_path: PathLike,
    *,
    page_separator: str = "\n\n",
    strip: bool = True,
) -> str:
    """
    Extract combined text from all pages in a PDF.
    """
    page_items = extract_text_by_page(pdf_path, strip=strip, skip_empty=False)
    return page_separator.join(item.text for item in page_items)


def extract_text_from_many_pdfs(
    pdf_paths: List[PathLike],
    *,
    page_separator: str = "\n\n",
    continue_on_error: bool = False,
) -> List[dict]:
    """
    Extract text from multiple PDFs.

    Returns items in the form:
    {
        "path": "<pdf path>",
        "text": "<combined extracted text>",
        "error": "<error message or None>"
    }
    """
    results: List[dict] = []

    for pdf_path in pdf_paths:
        path_str = str(pdf_path)
        try:
            text = extract_text(pdf_path, page_separator=page_separator)
            results.append({"path": path_str, "text": text, "error": None})
        except Exception as exc:
            if not continue_on_error:
                raise
            results.append({"path": path_str, "text": "", "error": str(exc)})

    return results


def extract_text_from_pdf_bytes(pdf_bytes: bytes, *, strip: bool = True) -> str:
    """
    Extract combined text from raw PDF bytes.
    """
    try:
        from io import BytesIO
    except Exception as exc:
        raise PDFExtractionError("Failed to initialize in-memory PDF stream.") from exc

    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except Exception as exc:
            raise PDFExtractionError(
                "No supported PDF library found. Install 'pypdf' (recommended) "
                "or 'PyPDF2' to enable extraction."
            ) from exc

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception as exc:
        raise PDFExtractionError("Failed to read PDF from bytes.") from exc

    texts: List[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if strip:
            page_text = page_text.strip()
        texts.append(page_text)
    return "\n\n".join(texts)
