# app/services/extractor.py
import tempfile
import os
from pathlib import Path
from loguru import logger

from app.services.storage_manager import StorageManager

# Optional imports
try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except Exception:
    _HAS_FITZ = False

try:
    import docx  # python-docx
    _HAS_DOCX = True
except Exception:
    _HAS_DOCX = False


class Extractor:
    """
    Wrapper class for text extraction from local files and Azure blobs.
    Compatible with process.py usage.
    """

    def extract_text(self, local_path: str) -> str:
        """Extract text from a local file (.pdf, .docx, .txt, .md)."""
        return self._extract_text_from_local(local_path)

    def extract_text_from_blob(self, blob_path: str) -> str:
        """Download a blob from Azure and extract text."""
        return self._extract_text_from_blob(blob_path)

    # -------------------- Internal methods --------------------
    def _read_text_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            try:
                with open(path, "r", encoding="latin-1", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read text file {path}: {e}")
                return ""

    def _extract_pdf(self, path: str) -> str:
        if not _HAS_FITZ:
            raise RuntimeError("PyMuPDF (fitz) not installed. Run `pip install pymupdf`.")
        text_parts = []
        try:
            with fitz.open(path) as pdf:
                for page in pdf:
                    try:
                        text = page.get_text("text")
                    except Exception:
                        text = page.get_text()
                    if text:
                        text_parts.append(text)
        except Exception as e:
            logger.error(f"Error extracting PDF {path}: {e}")
            return ""
        return "\n".join(text_parts)

    def _extract_docx(self, path: str) -> str:
        if not _HAS_DOCX:
            raise RuntimeError("python-docx not installed. Run `pip install python-docx`.")
        try:
            doc = docx.Document(path)
            paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error extracting DOCX {path}: {e}")
            return ""

    def _extract_text_from_local(self, local_path: str) -> str:
        p = Path(local_path)
        ext = p.suffix.lower()

        if ext in [".txt", ".md", ".text"]:
            return self._read_text_file(local_path)
        if ext == ".pdf":
            return self._extract_pdf(local_path)
        if ext in [".docx"]:
            return self._extract_docx(local_path)

        # fallback
        try:
            return self._read_text_file(local_path)
        except Exception as e:
            logger.error(f"Unsupported file type or extraction failed for {local_path}: {e}")
            return ""

    def _extract_text_from_blob(self, blob_path: str) -> str:
        storage = StorageManager()

        suffix = Path(blob_path).suffix or ""
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_file.close()
        tmp_path = tmp_file.name

        try:
            storage.download_file(blob_path, tmp_path)
            text = self._extract_text_from_local(tmp_path)
            if not text:
                logger.warning(f"No text extracted from blob: {blob_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from blob {blob_path}: {e}", exc_info=True)
            return ""
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
