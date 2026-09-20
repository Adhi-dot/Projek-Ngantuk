"""Code assignment assessor: run a Python solution against .in/.out test cases.

Reuse of the Personal Code Assessor concept, adapted for MabaOps:
- Each case directory contains pairs like ``case1.in`` and ``case1.out``.
- The solution is executed with a per-case timeout (default 2 seconds).
- Results include passed/failed/timeouts and an optional markdown report.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 2.0
REPORTS_DIR = "reports"


@dataclass
class CaseResult:
    name: str
    status: str  # "passed" | "failed" | "timeout" | "error"
    duration_ms: int = 0
    detail: str = ""


@dataclass
class AssessmentResult:
    target_file: str
    cases_dir: str
    passed: int = 0
    failed: int = 0
    timeouts: int = 0
    errors: int = 0
    cases: list[CaseResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.timeouts + self.errors

    @property
    def score(self) -> int:
        if self.total == 0:
            return 0
        return int(round(self.passed / self.total * 100))


def discover_cases(cases_dir: Path) -> list[tuple[str, Path, Path]]:
    """Return (case_name, input_path, expected_output_path) sorted by name."""

    if not cases_dir.is_dir():
        raise ValueError(f"Directory test case tidak ditemukan: {cases_dir}")

    pairs: list[tuple[str, Path, Path]] = []
    for input_path in sorted(cases_dir.glob("*.in")):
        expected_path = input_path.with_suffix(".out")
        if expected_path.exists():
            pairs.append((input_path.stem, input_path, expected_path))
    if not pairs:
        raise ValueError(
            f"Tidak ada pasangan .in/.out di {cases_dir}. "
            "Struktur yang diharapkan: case1.in + case1.out, case2.in + case2.out, dst."
        )
    return pairs


def run_case(solution: Path, case_name: str, input_path: Path, expected_path: Path, timeout: float) -> CaseResult:
    stdin_data = input_path.read_text(encoding="utf-8")
    expected = expected_path.read_text(encoding="utf-8").strip()

    # Minimal safe environment to prevent leaking host secrets/tokens to untrusted solution script
    safe_env = {
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PATH": os.environ.get("PATH", ""),
        "PATHEXT": os.environ.get("PATHEXT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "PYTHONIOENCODING": "utf-8",
    }

    start = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, str(solution)],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=safe_env,
        )
    except subprocess.TimeoutExpired:
        duration_ms = int((time.monotonic() - start) * 1000)
        return CaseResult(name=case_name, status="timeout", duration_ms=duration_ms)
    except OSError as error:
        duration_ms = int((time.monotonic() - start) * 1000)
        return CaseResult(name=case_name, status="error", duration_ms=duration_ms, detail=str(error))

    duration_ms = int((time.monotonic() - start) * 1000)
    actual = (proc.stdout or "").strip()

    if proc.returncode != 0:
        return CaseResult(
            name=case_name,
            status="error",
            duration_ms=duration_ms,
            detail=(proc.stderr or "unknown error").strip()[-500:],
        )
    if actual == expected:
        return CaseResult(name=case_name, status="passed", duration_ms=duration_ms)
    return CaseResult(
        name=case_name,
        status="failed",
        duration_ms=duration_ms,
        detail=f"expected: {expected!r} | got: {actual!r}",
    )


def assess_solution(target_file: Path, cases_dir: Path, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> AssessmentResult:
    if not target_file.is_file():
        raise ValueError(f"File solusi tidak ditemukan: {target_file}")

    result = AssessmentResult(target_file=str(target_file), cases_dir=str(cases_dir))
    for case_name, input_path, expected_path in discover_cases(cases_dir):
        case_result = run_case(target_file, case_name, input_path, expected_path, timeout)
        result.cases.append(case_result)
        if case_result.status == "passed":
            result.passed += 1
        elif case_result.status == "timeout":
            result.timeouts += 1
        elif case_result.status == "failed":
            result.failed += 1
        else:
            result.errors += 1
    return result


def write_report(result: AssessmentResult, reports_dir: Path, label: str | None = None) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    raw_label = label or Path(result.target_file).stem
    safe_label = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_label)
    report_path = reports_dir / f"{safe_label}-{stamp}.md"

    lines = [
        "# MabaOps Assessment Report",
        "",
        f"- Target: `{result.target_file}`",
        f"- Test cases: `{result.cases_dir}`",
        f"- Waktu: {datetime.now().isoformat(timespec='seconds')}",
        f"- Skor: **{result.score}** ({result.passed}/{result.total} passed)",
        f"- Failed: {result.failed} | Timeouts: {result.timeouts} | Errors: {result.errors}",
        "",
        "| Case | Status | Durasi | Detail |",
        "|---|---|---|---|",
    ]
    for case in result.cases:
        detail = case.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {case.name} | {case.status} | {case.duration_ms}ms | {detail or '-'} |")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
