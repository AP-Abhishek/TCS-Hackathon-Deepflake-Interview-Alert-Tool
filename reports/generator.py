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
"""

import json
from pathlib import Path
from datetime import datetime


class ReportResult(str):
    """Result object that acts as a string (json_path) and supports dict indexing."""
    def __new__(cls, json_path: str, markdown_path: str):
        instance = super().__new__(cls, json_path)
        instance.json_path = json_path
        instance.markdown_path = markdown_path
        return instance

    def __getitem__(self, key):
        if key == "json_path":
            return self.json_path
        elif key == "markdown_path":
            return self.markdown_path
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "json_path":
            return self.json_path
        elif key == "markdown_path":
            return self.markdown_path
        return default


def save_report(report_data: dict, output_dir: str = "reports/output") -> ReportResult:
    """
    Save both a JSON and Markdown audit report.

    Parameters
    ----------
    report_data : dict
        Expected keys:
        - skills: list[str]          (skills tested)
        - questions: list[str]       (questions asked)
        - final_score: int           (0-100)
        - status: str                ("CLEAN" | "SUSPICIOUS" | "HIGH_RISK")
        - total_infractions: int
        - infractions_log: list[dict]  (each: {timestamp, type, score_at_time})
        - interview_duration_sec: float (optional)
    output_dir : str
        Directory to write report files into.

    Returns
    -------
    ReportResult (string containing json_path, with ["json_path"] and ["markdown_path"] access)
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 1. Save JSON report ──────────────────────────────────────────
    json_file = out_path / f"interview_report_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # ── 2. Generate Markdown audit report ────────────────────────────
    md_file = out_path / f"interview_audit_{timestamp}.md"
    md_content = _build_markdown(report_data, timestamp)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[Audit Report] JSON  -> {json_file}")
    print(f"[Audit Report] MD    -> {md_file}")

    return ReportResult(str(json_file), str(md_file))


# ─────────────────────────── PRIVATE HELPERS ─────────────────────────────


def _build_markdown(data: dict, timestamp: str) -> str:
    """Assemble a clean, readable Markdown audit report."""

    score = data.get("final_integrity_score", data.get("final_score", "N/A"))
    status = data.get("integrity_classification", data.get("status", "UNKNOWN"))
    skills = data.get("skills_tested", data.get("skills", []))
    questions = data.get("questions_asked", data.get("questions", []))
    infractions = data.get("infractions_timeline", data.get("infractions_log", []))
    total_infractions = data.get("total_infractions_flagged", data.get("total_infractions", len(infractions)))
    duration = data.get("interview_duration_sec", None)

    # Status badge / emoji
    status_icon = {"CLEAN": "✅", "SUSPICIOUS": "⚠️", "HIGH_RISK": "🚨"}.get(status, "❓")

    lines = []
    lines.append("# 🛡️ AI Proctored Interview — Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if duration is not None:
        mins, secs = divmod(int(duration), 60)
        lines.append(f"**Interview Duration:** {mins}m {secs}s")
    lines.append("")

    # ── Integrity Score ──────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Integrity Score")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|:---|:---|")
    lines.append(f"| **Final Score** | **{score}%** |")
    lines.append(f"| **Classification** | {status_icon} **{status}** |")
    lines.append(f"| **Total Infractions** | {total_infractions} |")
    lines.append("")

    # Score bar visualisation (text-based)
    if isinstance(score, (int, float)):
        filled = int(score / 5)
        empty = 20 - filled
        bar_char = "█" * filled + "░" * empty
        lines.append(f"```")
        lines.append(f"Score: [{bar_char}] {score}%")
        lines.append(f"```")
        lines.append("")

    # ── Skills Tested ────────────────────────────────────────────────
    if skills:
        lines.append("---")
        lines.append("")
        lines.append("## 🎯 Skills Tested")
        lines.append("")
        for skill in skills:
            lines.append(f"- {skill}")
        lines.append("")

    # ── Questions Asked ──────────────────────────────────────────────
    if questions:
        lines.append("---")
        lines.append("")
        lines.append("## 📝 Interview Questions")
        lines.append("")
        for i, q in enumerate(questions, 1):
            lines.append(f"**Q{i}.** {q}")
            lines.append("")

    # ── Infractions Timeline ─────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## 🚩 Infraction Timeline")
    lines.append("")

    if infractions:
        lines.append("| # | Time | Violation | Score at Time |")
        lines.append("|:---|:---|:---|:---|")
        for i, inf in enumerate(infractions, 1):
            ts = inf.get("timestamp", "—")
            desc = inf.get("type", "Unknown")
            score_at = inf.get("score_at_time", "—")
            lines.append(f"| {i} | `{ts}` | {desc} | {score_at}% |")
        lines.append("")
    else:
        lines.append("_No infractions recorded. The candidate maintained a clean session._")
        lines.append("")

    # ── Summary & Recommendation ─────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## 📋 Summary")
    lines.append("")

    if status == "CLEAN":
        lines.append("> ✅ **CLEAN** — No significant anomalies detected during the interview.")
        lines.append("> The candidate maintained consistent eye contact, no unauthorized audio activity,")
        lines.append("> and a single-person presence throughout the session.")
    elif status == "SUSPICIOUS":
        lines.append("> ⚠️ **SUSPICIOUS** — Moderate anomalies were detected during the interview.")
        lines.append("> Review the infraction timeline above. Consider a follow-up round or manual review")
        lines.append("> of the flagged timestamps.")
    else:
        lines.append("> 🚨 **HIGH RISK** — Significant cheating indicators were detected.")
        lines.append("> Strong recommendation to invalidate this session or conduct a re-interview")
        lines.append("> under stricter proctoring conditions.")
    lines.append("")

    lines.append("---")
    lines.append("*Report generated by AI Proctored Interview Platform*")
    lines.append("")

    return "\n".join(lines)
