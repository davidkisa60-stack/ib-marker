"""Document text extraction and deterministic pre-checks."""

from __future__ import annotations

import io
import re
import shutil
import subprocess
import tempfile
from typing import Any

MAX_CHARS = 90_000  # characters of document text passed to the model


class ExtractionError(Exception):
    pass


def _docx_text(data: bytes) -> tuple[str, list[str]]:
    import docx  # python-docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    warnings: list[str] = []
    document = docx.Document(io.BytesIO(data))
    parts: list[str] = []
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            para = Paragraph(child, document)
            txt = para.text.strip()
            if not txt:
                continue
            style = (para.style.name if para.style is not None else "") or ""
            if style.lower().startswith("heading") or style.lower() == "title":
                parts.append(f"\n## {txt}\n")
            else:
                parts.append(txt)
        elif tag == "tbl":
            table = Table(child, document)
            rows = []
            for row in table.rows:
                cells = []
                seen = set()
                for cell in row.cells:
                    if id(cell._tc) in seen:
                        continue
                    seen.add(id(cell._tc))
                    cells.append(" ".join(cell.text.split()))
                rows.append(" | ".join(cells))
            parts.append("[TABLE]\n" + "\n".join(rows) + "\n[/TABLE]")
    # footnotes are not exposed by python-docx; note if the package contains them
    try:
        names = [p.partname for p in document.part.package.parts]
        if any("footnotes" in str(n) for n in names):
            warnings.append("The document contains footnotes, which could not be extracted; citations in footnotes may be missing from the text.")
        if any("/media/" in str(n) for n in names):
            warnings.append("Images in the document were not analysed (graphs, diagrams and photographs are judged only from their captions and surrounding text).")
    except Exception:
        pass
    return "\n".join(parts), warnings


def _pdf_text(data: bytes) -> tuple[str, list[str], int]:
    from pypdf import PdfReader

    warnings: list[str] = []
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:  # pragma: no cover
            raise ExtractionError("The PDF is password protected.") from exc
    pages: list[str] = []
    empty = 0
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if len(txt.strip()) < 20:
            empty += 1
        pages.append(f"\n[PAGE {i + 1}]\n{txt.strip()}")
    n = len(reader.pages)
    if n and empty / n > 0.5:
        warnings.append("More than half of the PDF pages contain little or no extractable text. The file may be scanned; run OCR before uploading for a reliable analysis.")
    elif empty:
        warnings.append(f"{empty} of {n} PDF pages contained little or no extractable text (possibly images or figures).")
    return "\n".join(pages), warnings, n


def _legacy_doc_text(data: bytes) -> tuple[str, list[str]]:
    """Convert a binary .doc using antiword or LibreOffice if available."""
    if shutil.which("antiword"):
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            res = subprocess.run(["antiword", tmp.name], capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout, ["Converted from legacy .doc with antiword; formatting and tables may be simplified."]
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        with tempfile.TemporaryDirectory() as tmpdir:
            src = f"{tmpdir}/input.doc"
            with open(src, "wb") as fh:
                fh.write(data)
            subprocess.run([soffice, "--headless", "--convert-to", "docx", "--outdir", tmpdir, src],
                           capture_output=True, timeout=120)
            try:
                with open(f"{tmpdir}/input.docx", "rb") as fh:
                    text, w = _docx_text(fh.read())
                return text, ["Converted from legacy .doc with LibreOffice."] + w
            except FileNotFoundError:
                pass
    raise ExtractionError("Legacy .doc files cannot be read on this server. Save the document as .docx or PDF and upload again.")


def extract_text(filename: str, data: bytes) -> dict[str, Any]:
    name = (filename or "").lower()
    pages = None
    if name.endswith(".docx"):
        text, warnings = _docx_text(data)
        kind = "docx"
    elif name.endswith(".pdf") or data[:5] == b"%PDF-":
        text, warnings, pages = _pdf_text(data)
        kind = "pdf"
    elif name.endswith(".doc"):
        text, warnings = _legacy_doc_text(data)
        kind = "doc"
    elif name.endswith((".txt", ".md", ".rtf")):
        text = data.decode("utf-8", errors="replace")
        if name.endswith(".rtf"):
            text = re.sub(r"\\[a-z]+-?\d* ?|[{}]", "", text)
        warnings = []
        kind = "text"
    else:
        raise ExtractionError("Unsupported file type. Upload a .docx, .pdf, .txt or .md file.")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text).strip()
    if not text:
        raise ExtractionError("No readable text was found in the document.")

    truncated = False
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        truncated = True
        warnings.append(f"The document is very long; only the first {MAX_CHARS:,} characters were analysed.")

    return {"text": text, "kind": kind, "pages": pages, "warnings": warnings, "truncated": truncated,
            "word_count": count_words(text)}


_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-]*")


def count_words(text: str) -> int:
    body = re.sub(r"\[/?TABLE\]|\[PAGE \d+\]", " ", text)
    return len(_WORD_RE.findall(body))


def precheck(text: str, rubric: dict[str, Any], word_count: int) -> list[dict[str, str]]:
    """Deterministic formal checks shown alongside the AI analysis."""
    checks: list[dict[str, str]] = []
    low = text.lower()

    limit = rubric.get("word_limit")
    if limit:
        if word_count > limit * 1.08:
            status, detail = "warn", f"About {word_count:,} words extracted against a limit of {limit:,}. The count includes headings, tables and references, which the IB usually excludes, but the excess looks substantial. Examiners stop reading at the limit."
        elif word_count > limit:
            status, detail = "info", f"About {word_count:,} words extracted against a limit of {limit:,}. Tables, captions and references are included in this estimate, so the body may still be within the limit."
        elif word_count < limit * 0.4:
            status, detail = "info", f"About {word_count:,} words extracted; this is well under the {limit:,}-word limit, which may indicate a partial document, a short task, or extraction problems."
        else:
            status, detail = "ok", f"About {word_count:,} words extracted (limit {limit:,})."
        checks.append({"label": "Word count", "status": status, "detail": detail})
    else:
        checks.append({"label": "Word count", "status": "info", "detail": f"About {word_count:,} words extracted."})

    def has(*patterns: str) -> bool:
        return any(re.search(p, low) for p in patterns)

    rq = has(r"research question", r"\bquestion:\s", r"to what extent", r"\bhow (?:does|do|did|far|effectively|successfully)\b", r"\binquiry question", r"\bfieldwork question")
    checks.append({"label": "Research question", "status": "ok" if rq else "warn",
                   "detail": "A research question or question-style title was found." if rq else "No explicit research question was detected. Most IB tasks require one to be stated clearly near the start."})

    bib = has(r"\bbibliography\b", r"\breferences\b", r"\bworks cited\b", r"\bsources consulted\b", r"\breference list\b")
    checks.append({"label": "Bibliography or references", "status": "ok" if bib else "warn",
                   "detail": "A bibliography, references or works-cited section heading was found." if bib else "No bibliography or references heading was detected. Unreferenced work risks academic-integrity issues and loses marks for presentation or communication."})

    cites = len(re.findall(r"\(\s*[A-Z][A-Za-z\-]+(?:\s+(?:et al\.|and|&)\s*[A-Z][A-Za-z\-]*)?,?\s*(?:19|20)\d{2}[a-z]?\s*(?:[:,]\s*p{0,2}\.?\s*\d+)?\)", text))
    cites += len(re.findall(r"\[\d{1,3}\]", text))
    urls = len(re.findall(r"https?://", text))
    checks.append({"label": "Citations", "status": "ok" if (cites + urls) >= 3 else "info",
                   "detail": f"About {cites} in-text citations and {urls} web links were detected." if (cites + urls) else "No in-text citations or links were detected (footnote citations in Word files are not extractable)."})

    comp = rubric.get("component")
    if comp == "Extended Essay":
        refl = has(r"\brppf\b", r"\brpf\b", r"reflections? on planning and progress", r"reflection and progress form", r"reflective statement", r"\bviva voce\b", r"reflection session")
        checks.append({"label": "Reflection form (criterion E)", "status": "ok" if refl else "warn",
                       "detail": "Reflection text (RPPF or RPF) appears to be included." if refl else "No reflection form text was found. Criterion E can only be marked from the RPPF or RPF; append it to the file or paste it in the notes."})
        toc = has(r"\b(?:table of )?contents\b")
        checks.append({"label": "Contents page", "status": "ok" if toc else "info",
                       "detail": "A contents page was found." if toc else "No contents page was detected (a required formal element of the extended essay)."})
    if comp == "Theory of Knowledge" and rubric.get("id") == "tok-exhibition":
        objs = len(re.findall(r"\bobject\s*(?:1|2|3|one|two|three)\b", low))
        checks.append({"label": "Three objects", "status": "ok" if objs >= 3 else "warn",
                       "detail": "Three labelled objects were found." if objs >= 3 else "Fewer than three labelled objects were detected; check that each object is identified."})
        prompt = has(r"\bprompt\b", r"ia prompt")
        checks.append({"label": "IA prompt", "status": "ok" if prompt else "warn",
                       "detail": "The IA prompt appears to be stated." if prompt else "The selected IA prompt was not found; it must be stated verbatim."})

    figs = len(re.findall(r"\b(?:figure|fig\.|table|graph|chart|diagram)\s*\d+", low))
    tables = text.count("[TABLE]")
    checks.append({"label": "Figures and tables", "status": "info",
                   "detail": f"About {figs} numbered figure/table references and {tables} extracted tables were found. Images themselves are not analysed."})

    heads = len(re.findall(r"^## ", text, flags=re.M))
    if heads:
        checks.append({"label": "Structure", "status": "ok", "detail": f"{heads} headings detected in the Word document."})
    return checks
