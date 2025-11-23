"""Compile Work Log and presentation metadata into JSON for the React web app."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyPDF2 import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = PROJECT_ROOT / "public" / "resources"
WORK_LOGS_DIR = RESOURCES_DIR / "work_logs"
PRESENTATIONS_DIR = RESOURCES_DIR / "presentations"
DATA_OUTPUT_PATH = PROJECT_ROOT / "src" / "data" / "content.json"

WORK_LOGS_WEB_PATH = "resources/work_logs"
PRESENTATIONS_WEB_PATH = "resources/presentations"

DATE_PATTERN = re.compile(r"(\d{2}_\d{2}_\d{4})")
UNKNOWN_SORT_VALUE = float("-inf")


def parse_date_from_filename(file_name: str) -> Optional[datetime]:
    """Extract dd_mm_yyyy dates embedded within Work Log filenames."""
    match = DATE_PATTERN.search(file_name)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%d_%m_%Y")


def parse_pdf_timestamp(file_name: str) -> Optional[datetime]:
    """Extract yyyy-mm-dd_hh-mm-ss timestamps from presentation filenames."""
    candidate = file_name[-23:-4]
    try:
        return datetime.strptime(candidate, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None


def count_pdf_slides(pdf_path: Path) -> int:
    """Return the number of pages in the provided PDF."""
    try:
        with pdf_path.open("rb") as pdf_file:
            reader = PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as exc:
        print(f"Error reading {pdf_path}: {exc}")
        return 0


def build_presentation_display_name(file_name: str) -> str:
    """Drop the trailing timestamp that gets appended to exported files."""
    return file_name[:-24] if len(file_name) > 23 else file_name


def sort_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort by the helper _sort_key and strip it before returning data."""
    entries.sort(key=lambda item: item.get("_sort_key", UNKNOWN_SORT_VALUE), reverse=True)
    for entry in entries:
        entry.pop("_sort_key", None)
    return entries


def collect_work_logs() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if not WORK_LOGS_DIR.exists():
        print(f"Work logs directory not found: {WORK_LOGS_DIR}")
        return entries

    for html_file in WORK_LOGS_DIR.iterdir():
        if html_file.suffix.lower() != ".html":
            continue

        created = parse_date_from_filename(html_file.name)

        entries.append(
            {
                "fileName": html_file.name,
                "title": html_file.name,
                "url": f"{WORK_LOGS_WEB_PATH}/{html_file.name}",
                "createdDate": created.strftime("%Y-%m-%d") if created else None,
                "_sort_key": created.timestamp() if created else UNKNOWN_SORT_VALUE,
            }
        )

    return sort_entries(entries)


def collect_presentations() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if not PRESENTATIONS_DIR.exists():
        print(f"Presentations directory not found: {PRESENTATIONS_DIR}")
        return entries

    for pdf_file in PRESENTATIONS_DIR.iterdir():
        if pdf_file.suffix.lower() != ".pdf":
            continue

        created = parse_pdf_timestamp(pdf_file.name)
        if created is None:
            print(f"Failed to extract date from PDF: {pdf_file.name}")

        entries.append(
            {
                "fileName": pdf_file.name,
                "title": build_presentation_display_name(pdf_file.name),
                "url": f"{PRESENTATIONS_WEB_PATH}/{pdf_file.name}",
                "slides": count_pdf_slides(pdf_file),
                "createdDate": created.strftime("%Y-%m-%d") if created else None,
                "_sort_key": created.timestamp() if created else UNKNOWN_SORT_VALUE,
            }
        )

    return sort_entries(entries)


def main() -> None:
    work_logs = collect_work_logs()
    presentations = collect_presentations()

    DATA_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "workLogs": work_logs,
        "presentations": presentations,
    }

    with DATA_OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2)
        output_file.write("\n")

    print(
        f"Wrote {len(work_logs)} work logs and {len(presentations)} presentations to {DATA_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
