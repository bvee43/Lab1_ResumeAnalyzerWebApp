"""
parse.py

Utilities for reading a résumé (PDF) and a job description (plain text)
into clean strings suitable for downstream processing.
"""

import re
import sys

from pypdf import PdfReader

MAX_RESUME_CHARS = 24_000
MIN_RESUME_CHARS = 200
MIN_JD_CHARS = 100
MAX_RESUME_PAGES = 2


def read_resume_pdf(path: str) -> str:
    """
    Read a résumé PDF file and return its extracted text.

    Args:
        path: Path to the PDF file.

    Returns:
        The extracted, cleaned text of the résumé.

    Raises:
        ValueError: If the file cannot be found or opened, if the
            extracted text is too short (suggesting an image-based PDF),
            or for any other failure while reading the PDF.
    """
    try:
        reader = PdfReader(path)
    except FileNotFoundError as exc:
        raise ValueError(f"Résumé PDF not found at path: {path!r}") from exc
    except Exception as exc:
        raise ValueError(f"Could not open résumé PDF at {path!r}: {exc}") from exc

    num_pages = len(reader.pages)
    if num_pages > MAX_RESUME_PAGES:
        print(
            f"Warning: résumé PDF at {path!r} has {num_pages} pages "
            f"(expected {MAX_RESUME_PAGES} or fewer).",
            file=sys.stderr,
        )

    try:
        page_texts = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(f"Could not extract text from résumé PDF at {path!r}: {exc}") from exc

    text = "\n\n".join(page_texts)

    # Collapse runs of 3+ blank lines down to 2.
    text = re.sub(r"\n{3,}", "\n\n", text)

    stripped_len = len(text.strip())
    if stripped_len < MIN_RESUME_CHARS:
        raise ValueError(
            f"Extracted text from résumé PDF at {path!r} is too short "
            f"({stripped_len} characters); the PDF may be image-based "
            f"and require OCR."
        )

    if len(text) > MAX_RESUME_CHARS:
        print(
            f"Warning: résumé text from {path!r} is {len(text)} characters; "
            f"truncating to {MAX_RESUME_CHARS} characters.",
            file=sys.stderr,
        )
        text = text[:MAX_RESUME_CHARS]

    return text


def read_jd_text(path: str) -> str:
    """
    Read a job description from a UTF-8 plain text file.

    Args:
        path: Path to the text file.

    Returns:
        The file's contents.

    Raises:
        ValueError: If the file cannot be found, or if the content is
            fewer than 100 characters after stripping whitespace.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as exc:
        raise ValueError(f"Job description file not found at path: {path!r}") from exc
    except Exception as exc:
        raise ValueError(f"Could not read job description file at {path!r}: {exc}") from exc

    stripped = content.strip()
    if len(stripped) < MIN_JD_CHARS:
        raise ValueError(
            f"Job description at {path!r} is too short "
            f"({len(stripped)} characters after stripping whitespace); "
            f"expected at least {MIN_JD_CHARS} characters."
        )

    return content