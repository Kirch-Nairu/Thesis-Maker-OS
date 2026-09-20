from __future__ import annotations

from pathlib import Path


def extract_text(path: str | Path) -> str:
    source = Path(path)
    suffix = source.suffix.lower()

    if suffix in {".txt", ".md", ".markdown"}:
        return source.read_text(encoding="utf-8")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF support is optional. Install with: pip install -e '.[pdf]'"
            ) from exc
        reader = PdfReader(str(source))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)

    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError(
                "DOCX support is optional. Install with: pip install -e '.[docx]'"
            ) from exc
        document = Document(str(source))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError(f"Unsupported manuscript type: {suffix or '<none>'}")
