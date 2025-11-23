#!/usr/bin/env python3
"""Generate a full-text search index for Work Logs and Presentations."""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = PROJECT_ROOT / "public" / "resources"
WORK_LOGS_DIR = RESOURCES_DIR / "work_logs"
PRESENTATIONS_DIR = RESOURCES_DIR / "presentations"
OUTPUT_PATH = PROJECT_ROOT / "src" / "data" / "search-index.json"

DATE_PATTERN = re.compile(r"(\d{2}_\d{2}_\d{4})")
WORK_LOG_TIMESTAMP_FORMAT = "%d_%m_%Y"
PRESENTATION_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
WORD_PATTERN = re.compile(r"\w+")

logging.getLogger("PyPDF2").setLevel(logging.ERROR)


def normalize_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces."""
    return re.sub(r"\s+", " ", text).strip()


def extract_html_text(path: Path) -> str:
    """Read and clean text from a Work Log HTML file."""
    with path.open("r", encoding="utf-8", errors="ignore") as source:
        soup = BeautifulSoup(source, "html.parser")
        # Drop script/style tags
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ")
        return normalize_text(text)


def extract_pdf_text(path: Path) -> str:
    """Read text from a PDF file."""
    text_chunks: List[str] = []
    try:
        reader = PdfReader(str(path), strict=False)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to read PDF {path}: {exc}")
        return ""

    for page in reader.pages:
        try:
            text_chunks.append(page.extract_text() or "")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Failed to extract text from {path} page: {exc}")
    return normalize_text(" ".join(text_chunks))


@dataclass
class SearchEntry:
    kind: str
    title: str
    fileName: str
    url: str
    createdDate: Optional[str]
    text: str

    def token_count(self) -> int:
        return len(WORD_PATTERN.findall(self.text))


def parse_work_log_date(file_name: str) -> Optional[str]:
    match = DATE_PATTERN.search(file_name)
    if not match:
        return None
    try:
        dt = datetime.strptime(match.group(1), WORK_LOG_TIMESTAMP_FORMAT)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def parse_presentation_date(file_name: str) -> Optional[str]:
    candidate = file_name[-23:-4]
    try:
        dt = datetime.strptime(candidate, PRESENTATION_TIMESTAMP_FORMAT)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def collect_work_log_entries() -> List[SearchEntry]:
    entries: List[SearchEntry] = []
    if not WORK_LOGS_DIR.exists():
        return entries

    for html_file in WORK_LOGS_DIR.iterdir():
        if html_file.suffix.lower() != ".html":
            continue
        try:
            text = extract_html_text(html_file)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Failed to parse {html_file}: {exc}")
            continue
        entries.append(
            SearchEntry(
                kind="work-log",
                title=html_file.name,
                fileName=html_file.name,
                url=f"resources/work_logs/{html_file.name}",
                createdDate=parse_work_log_date(html_file.name),
                text=text,
            )
        )
    return entries

def collect_presentation_entries() -> List[SearchEntry]:
    entries: List[SearchEntry] = []
    if not PRESENTATIONS_DIR.exists():
        return entries

    for pdf_file in PRESENTATIONS_DIR.iterdir():
        if pdf_file.suffix.lower() != ".pdf":
            continue
        text = extract_pdf_text(pdf_file)
        entries.append(
            SearchEntry(
                kind="presentation",
                title=pdf_file.name,
                fileName=pdf_file.name,
                url=f"resources/presentations/{pdf_file.name}",
                createdDate=parse_presentation_date(pdf_file.name),
                text=text,
            )
        )
    return entries


def build_index() -> None:
    entries = collect_work_log_entries() + collect_presentation_entries()
    serialized = [
        {
            "kind": entry.kind,
            "title": entry.title,
            "fileName": entry.fileName,
            "url": entry.url,
            "createdDate": entry.createdDate,
            "text": entry.text,
            "textLength": entry.token_count(),
        }
        for entry in entries
    ]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as target:
        json.dump(serialized, target, indent=2)
        target.write("\n")
    print(f"Wrote {len(serialized)} search entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_index()
