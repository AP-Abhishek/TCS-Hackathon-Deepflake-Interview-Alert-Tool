"""
reports/generator.py
--------------------
Responsible: Person 4 (Cheating Scoring & Audit Reports)

TASK OBJECTIVE:
- Save interview proctoring summary to a timestamped JSON file and a readable Markdown summary report.
- Include:
  - Candidate Skills Tested
  - Final Integrity Score & Classification (CLEAN / SUSPICIOUS / HIGH_RISK)
  - Chronological list of infractions with timestamps
  - Questions asked during the interview

TODO for Person 4:
1. Implement `save_report(report_data, output_dir)` to dump a JSON file in `reports/output/`.
2. Generate a clean, readable Markdown audit file `interview_audit_<timestamp>.md`.
"""

import json
from pathlib import Path
from datetime import datetime


def save_report(report_data: dict, output_dir: str = "reports/output") -> str:
    """
    TODO:
    - Create output_dir if not exists.
    - Write report_data to interview_report_<timestamp>.json.
    - Return the path to the saved report.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = out_path / f"interview_report_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"[Audit Report] Saved to {file_path}")
    return str(file_path)
