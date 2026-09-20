from pathlib import Path

from typer.testing import CliRunner

import pytest

from mabaops.cli import app
from datetime import datetime, timedelta

runner = CliRunner()


def test_help_shows_mabaops():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "MabaOps" in result.output
    assert "today" in result.output
    assert "schedule" in result.output
    assert "task" in result.output


def test_init_demo_creates_data_files(tmp_path):
    data_dir = tmp_path / "data"

    result = runner.invoke(app, ["init", "--demo", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "MabaOps siap" in result.output
    assert (data_dir / "schedule.json").exists()
    assert (data_dir / "tasks.json").exists()
    assert (data_dir / "budget.json").exists()
    assert (data_dir / "budget_entries.json").exists()


def test_today_without_data_prompts_init(tmp_path):
    data_dir = tmp_path / "missing"

    result = runner.invoke(app, ["today", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Belum ada data MabaOps" in result.output
    assert "mabaops init --demo" in result.output


def test_today_with_demo_data_outputs_dashboard(tmp_path):
    data_dir = tmp_path / "data"
    init_result = runner.invoke(app, ["init", "--demo", "--data-dir", str(data_dir)])
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["today", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "MabaOps Today" in result.output
    assert "Algoritma" in result.output
    assert "Fokus" in result.output


def test_schedule_add_and_list(tmp_path):
    data_dir = tmp_path / "data"
    result = runner.invoke(
        app,
        [
            "schedule",
            "add",
            "--course-code",
            "IF102",
            "--course-name",
            "Struktur Data",
            "--day",
            "Senin",
            "--start",
            "09:00",
            "--end",
            "10:40",
            "--building",
            "Gedung C",
            "--room",
            "C301",
            "--notes",
            "Bawa laptop",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Jadwal ditambahkan" in result.output
    assert "Struktur Data" in result.output

    list_result = runner.invoke(app, ["schedule", "list", "--data-dir", str(data_dir)])

    assert list_result.exit_code == 0
    assert "Jadwal Kuliah" in list_result.output
    assert "IF102" in list_result.output
    assert "Struktur Data" in list_result.output
    assert "Gedung C C301" in list_result.output


def test_schedule_list_filters_by_day(tmp_path):
    data_dir = tmp_path / "data"
    runner.invoke(
        app,
        [
            "schedule",
            "add",
            "--course-code",
            "IF102",
            "--course-name",
            "Struktur Data",
            "--day",
            "Senin",
            "--start",
            "09:00",
            "--end",
            "10:40",
            "--data-dir",
            str(data_dir),
        ],
    )
    runner.invoke(
        app,
        [
            "schedule",
            "add",
            "--course-code",
            "MA101",
            "--course-name",
            "Kalkulus",
            "--day",
            "Selasa",
            "--start",
            "13:00",
            "--end",
            "14:40",
            "--data-dir",
            str(data_dir),
        ],
    )

    result = runner.invoke(app, ["schedule", "list", "--day", "Senin", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Struktur Data" in result.output
    assert "Kalkulus" not in result.output


def test_schedule_today_with_demo_data_outputs_today_schedule(tmp_path):
    data_dir = tmp_path / "data"
    init_result = runner.invoke(app, ["init", "--demo", "--data-dir", str(data_dir)])
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["schedule", "today", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Jadwal Hari Ini" in result.output
    assert "Algoritma" in result.output


def test_schedule_add_rejects_invalid_day(tmp_path):
    data_dir = tmp_path / "data"

    result = runner.invoke(
        app,
        [
            "schedule",
            "add",
            "--course-code",
            "IF999",
            "--course-name",
            "Kelas Misterius",
            "--day",
            "Funday",
            "--start",
            "09:00",
            "--end",
            "10:00",
            "--data-dir",
            str(data_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Hari tidak valid" in result.output


def test_task_add_list_and_status(tmp_path):
    data_dir = tmp_path / "data"

    # Add task
    add_res = runner.invoke(
        app,
        [
            "task",
            "add",
            "BasisData",
            "--due",
            "2026-09-30",
            "--estimate",
            "90",
            "--course",
            "IF103",
            "--data-dir",
            str(data_dir),
        ],
    )
    assert add_res.exit_code == 0
    assert "Tugas ditambahkan" in add_res.output

    # List tasks
    list_res = runner.invoke(app, ["task", "list", "--data-dir", str(data_dir)])
    assert list_res.exit_code == 0
    assert "BasisData" in list_res.output
    assert "IF103" in list_res.output

    # Start task
    tasks = load_tasks_direct(data_dir)
    task_id = tasks[0].id

    start_res = runner.invoke(app, ["task", "start", task_id[:4], "--data-dir", str(data_dir)])
    assert start_res.exit_code == 0
    assert "in_progress" in start_res.output or "Tugas dimulai" in start_res.output

    # Done task
    done_res = runner.invoke(app, ["task", "done", task_id[:4], "--data-dir", str(data_dir)])
    assert done_res.exit_code == 0
    assert "Tugas selesai" in done_res.output


def load_tasks_direct(data_dir):
    from mabaops.storage import load_tasks
    return load_tasks(data_dir)


def test_task_priority_sorting(tmp_path):
    data_dir = tmp_path / "data"
    from datetime import datetime, timedelta

    now = datetime.now()
    due_soon = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    due_far = (now + timedelta(days=20)).strftime("%Y-%m-%d")

    runner.invoke(app, ["task", "add", "TugasJauh", "--due", due_far, "--estimate", "30", "--data-dir", str(data_dir)])
    runner.invoke(app, ["task", "add", "TugasDeket", "--due", due_soon, "--estimate", "120", "--data-dir", str(data_dir)])

    tasks = load_tasks_direct(data_dir)

    assert tasks[0].title == "TugasDeket"
    assert tasks[0].priority_score > tasks[1].priority_score


def test_task_overdue_and_urgent_labels(tmp_path):
    data_dir = tmp_path / "data"
    from datetime import datetime, timedelta

    now = datetime.now()
    overdue = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    urgent = (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M")

    runner.invoke(app, ["task", "add", "TugasTelat", "--due", overdue, "--data-dir", str(data_dir)])
    runner.invoke(app, ["task", "add", "TugasDeket", "--due", urgent, "--data-dir", str(data_dir)])

    tasks = load_tasks_direct(data_dir)
    labels = {task.title: task.urgency_label for task in tasks}

    assert labels["TugasTelat"] == "OVERDUE"
    assert labels["TugasDeket"] == "URGENT"
    assert tasks[0].title == "TugasTelat"  # overdue ranks highest


def test_task_list_filters_by_status(tmp_path):
    data_dir = tmp_path / "data"
    from datetime import timedelta

    due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    runner.invoke(app, ["task", "add", "TugasA", "--due", due, "--data-dir", str(data_dir)])
    runner.invoke(app, ["task", "add", "TugasB", "--due", due, "--data-dir", str(data_dir)])

    tasks = load_tasks_direct(data_dir)
    runner.invoke(app, ["task", "start", tasks[0].id[:8], "--data-dir", str(data_dir)])

    list_res = runner.invoke(app, ["task", "list", "--status", "in_progress", "--data-dir", str(data_dir)])

    assert list_res.exit_code == 0
    assert "TugasA" in list_res.output
    assert "TugasB" not in list_res.output


def test_task_done_or_start_rejects_unknown_id(tmp_path):
    data_dir = tmp_path / "data"
    from datetime import timedelta

    due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    runner.invoke(app, ["task", "add", "TugasA", "--due", due, "--data-dir", str(data_dir)])

    result = runner.invoke(app, ["task", "done", "tidakada", "--data-dir", str(data_dir)])

    assert result.exit_code == 1
    assert "tidak ditemukan" in result.output.replace("\n", "")


def test_today_renders_top_priority_tasks(tmp_path):
    data_dir = tmp_path / "data"
    from datetime import datetime, timedelta

    now = datetime.now()
    due_soon = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    due_far = (now + timedelta(days=15)).strftime("%Y-%m-%d")

    runner.invoke(app, ["task", "add", "PrioTinggi", "--due", due_soon, "--estimate", "120", "--data-dir", str(data_dir)])
    runner.invoke(app, ["task", "add", "PrioRendah", "--due", due_far, "--estimate", "30", "--data-dir", str(data_dir)])

    tasks = load_tasks_direct(data_dir)
    runner.invoke(app, ["task", "done", tasks[0].id[:8], "--data-dir", str(data_dir)])

    result = runner.invoke(app, ["today", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "PrioRendah" in result.output

    # Done task tidak muncul lagi di deadline today
    done_titles = [task.title for task in load_tasks_direct(data_dir) if task.status == "done"]
    assert "PrioTinggi" in done_titles
    assert "PrioTinggi" not in result.output.split("Fokus:")[0].split("Deadline")[-1]


def test_budget_set_weekly_and_add_entries(tmp_path):
    data_dir = tmp_path / "data"

    set_res = runner.invoke(app, ["budget", "set-weekly", "500000", "--data-dir", str(data_dir)])
    assert set_res.exit_code == 0
    assert "Budget mingguan diset" in set_res.output

    expense_res = runner.invoke(
        app, ["budget", "add", "expense", "15000", "-c", "makan", "-n", "nasi ayam", "--data-dir", str(data_dir)]
    )
    assert expense_res.exit_code == 0
    assert "Pengeluaran dicatat" in expense_res.output

    income_res = runner.invoke(app, ["budget", "add", "income", "50000", "--data-dir", str(data_dir)])
    assert income_res.exit_code == 0
    assert "Pemasukan dicatat" in income_res.output


def test_budget_add_rejects_invalid_type_and_category(tmp_path):
    data_dir = tmp_path / "data"

    bad_type = runner.invoke(app, ["budget", "add", "transfer", "10000", "--data-dir", str(data_dir)])
    assert bad_type.exit_code == 1
    assert "Tipe entri tidak valid" in bad_type.output

    runner.invoke(app, ["budget", "set-weekly", "100000", "--data-dir", str(data_dir)])
    bad_cat = runner.invoke(app, ["budget", "add", "expense", "10000", "-c", "kuliner", "--data-dir", str(data_dir)])
    assert bad_cat.exit_code == 1
    assert "Kategori tidak valid" in bad_cat.output.replace("\n", "")


def test_budget_summary_safe_and_warning(tmp_path):
    data_dir = tmp_path / "data"

    runner.invoke(app, ["budget", "set-weekly", "700000", "--data-dir", str(data_dir)])
    runner.invoke(app, ["budget", "add", "expense", "5000", "--data-dir", str(data_dir)])

    safe_res = runner.invoke(app, ["budget", "summary", "--data-dir", str(data_dir)])
    assert safe_res.exit_code == 0
    assert "Aman" in safe_res.output

    # Deficit: pengeluaran melebihi budget -> perlu perhatian (deterministik)
    data_dir2 = tmp_path / "data2"
    runner.invoke(app, ["budget", "set-weekly", "3000", "--data-dir", str(data_dir2)])
    runner.invoke(app, ["budget", "add", "expense", "5000", "--data-dir", str(data_dir2)])

    warn_res = runner.invoke(app, ["budget", "summary", "--data-dir", str(data_dir2)])
    assert warn_res.exit_code == 0
    assert "Perlu perhatian" in warn_res.output


def test_budget_summary_without_budget_shows_setup_hint(tmp_path):
    data_dir = tmp_path / "data"

    result = runner.invoke(app, ["budget", "summary", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Budget mingguan belum diset" in result.output
    assert "budget set-weekly" in result.output


def test_dashboard_with_demo_data_outputs_panels(tmp_path):
    data_dir = tmp_path / "data"

    init_res = runner.invoke(app, ["init", "--demo", "--data-dir", str(data_dir)])
    assert init_res.exit_code == 0

    result = runner.invoke(app, ["dashboard", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Hari ini:" in result.output
    assert "Jadwal Hari Ini" in result.output
    assert "Deadline Prioritas" in result.output
    assert "Budget" in result.output
    assert "Fokus:" in result.output
    # Task dengan skor tertinggi (URGENT) tampil di dashboard
    assert "Tugas Array" in result.output


def test_dashboard_without_data_prompts_init(tmp_path):
    data_dir = tmp_path / "missing"

    result = runner.invoke(app, ["dashboard", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Belum ada data MabaOps" in result.output
    assert "mabaops init --demo" in result.output


def test_dashboard_budget_bar_and_left_amount(tmp_path):
    data_dir = tmp_path / "data"

    runner.invoke(app, ["budget", "set-weekly", "100000", "--data-dir", str(data_dir)])
    runner.invoke(app, ["budget", "add", "expense", "50000", "--data-dir", str(data_dir)])

    result = runner.invoke(app, ["dashboard", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Left: Rp 50.000" in result.output
    assert "50%" in result.output
    assert "#-----" in result.output  # progress bar ASCII-safe


@pytest.fixture
def assess_env(tmp_path, monkeypatch):
    """Prepare solution file, test cases dir, and isolated cwd for reports."""

    solution = tmp_path / "solution.py"
    cases_dir = tmp_path / "test_cases"
    cases_dir.mkdir()

    # Case 1: pass (2 + 3 = 5)
    (cases_dir / "case1.in").write_text("2\n3\n", encoding="utf-8")
    (cases_dir / "case1.out").write_text("5\n", encoding="utf-8")
    # Case 2: fail (expects 7, solution outputs wrong sum)
    (cases_dir / "case2.in").write_text("10\n20\n", encoding="utf-8")
    (cases_dir / "case2.out").write_text("7\n", encoding="utf-8")
    # Case 3: timeout (infinite loop on flag 999)
    (cases_dir / "case3.in").write_text("999\n0\n", encoding="utf-8")
    (cases_dir / "case3.out").write_text("0\n", encoding="utf-8")

    solution.write_text(
        "a = int(input())\n"
        "b = int(input())\n"
        "if a == 999:\n"
        "    while True:\n"
        "        pass\n"
        "print(a + b)\n",
        encoding="utf-8",
    )

    reports_dir = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)
    return solution, cases_dir, reports_dir


def test_assess_pass_fail_timeout_and_report(assess_env):
    solution, cases_dir, reports_dir = assess_env

    result = runner.invoke(app, ["assess", str(solution), "--cases", str(cases_dir), "--timeout", "1"])

    assert result.exit_code == 1  # ada case gagal
    assert "passed" in result.output
    assert "failed" in result.output
    assert "timeout" in result.output
    assert "Skor:" in result.output

    reports = list(reports_dir.glob("solution-*.md"))
    assert len(reports) == 1
    content = reports[0].read_text(encoding="utf-8")
    assert "Assessment Report" in content
    assert "case1" in content and "case3" in content


def test_assess_all_pass_exit_zero(tmp_path, monkeypatch):
    solution = tmp_path / "good.py"
    cases_dir = tmp_path / "test_cases"
    cases_dir.mkdir()
    (cases_dir / "case1.in").write_text("1\n2\n", encoding="utf-8")
    (cases_dir / "case1.out").write_text("3\n", encoding="utf-8")
    solution.write_text("print(int(input()) + int(input()))\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["assess", str(solution), "--cases", str(cases_dir)])

    assert result.exit_code == 0
    assert "1/1 passed" in result.output


def test_assess_missing_cases_dir(tmp_path, monkeypatch):
    solution = tmp_path / "ok.py"
    solution.write_text("print('hi')\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["assess", str(solution), "--cases", str(tmp_path / "tidak_ada")])

    assert result.exit_code == 1
    assert "tidak ditemukan" in result.output.replace("\n", "")


def test_schedule_delete(tmp_path):
    data_dir = tmp_path / "data"
    runner.invoke(
        app,
        [
            "schedule",
            "add",
            "-c",
            "IF102",
            "-n",
            "Struktur Data",
            "-d",
            "Senin",
            "--start",
            "09:00",
            "--end",
            "10:40",
            "--data-dir",
            str(data_dir),
        ],
    )
    # Delete by course code
    del_res = runner.invoke(app, ["schedule", "delete", "IF102", "--data-dir", str(data_dir)])
    assert del_res.exit_code == 0
    assert "Jadwal dihapus" in del_res.output
    assert "IF102" in del_res.output

    # Verify list is empty
    list_res = runner.invoke(app, ["schedule", "list", "--data-dir", str(data_dir)])
    assert "Belum ada jadwal" in list_res.output


def test_task_plan_heuristic(tmp_path):
    data_dir = tmp_path / "data"
    runner.invoke(
        app,
        [
            "task",
            "add",
            "Tugas Implementasi Graf",
            "--due",
            "2026-09-30",
            "--category",
            "coding",
            "--data-dir",
            str(data_dir),
        ],
    )
    tasks = load_tasks_direct(data_dir)
    plan_res = runner.invoke(app, ["task", "plan", tasks[0].id[:8], "--data-dir", str(data_dir)])
    assert plan_res.exit_code == 0
    assert "Rencana pengerjaan" in plan_res.output
    assert "Pahami soal" in plan_res.output

    # Verify subtasks persisted
    updated_tasks = load_tasks_direct(data_dir)
    assert len(updated_tasks[0].subtasks) > 0


def test_budget_summary_clean_currency_formatting(tmp_path):
    data_dir = tmp_path / "data"
    runner.invoke(app, ["budget", "set-weekly", "500000", "--data-dir", str(data_dir)])
    res = runner.invoke(app, ["budget", "summary", "--data-dir", str(data_dir)])
    assert res.exit_code == 0
    assert "Rp: Rp" not in res.output
    assert "Rp 500.000" in res.output


def test_today_budget_isolates_previous_week_entries(tmp_path):
    data_dir = tmp_path / "data"
    from mabaops.storage import init_storage, write_json, BUDGET_ENTRIES_FILE, BUDGET_FILE
    init_storage(data_dir)

    # Set weekly budget 500.000
    write_json(data_dir / BUDGET_FILE, {"weekly_budget": 500000, "currency": "IDR"})

    # Add old expense from 14 days ago (previous week)
    old_date = (datetime.now() - timedelta(days=14)).isoformat(timespec="seconds")
    write_json(
        data_dir / BUDGET_ENTRIES_FILE,
        [
            {
                "id": "old-entry",
                "type": "expense",
                "amount": 200000,
                "category": "makan",
                "note": "old food",
                "created_at": old_date,
            }
        ],
    )

    # In today command, spent this week should be 0 and left should be 500.000 (not 300.000)
    today_res = runner.invoke(app, ["today", "--data-dir", str(data_dir)])
    assert today_res.exit_code == 0
    assert "Left: Rp 500.000" in today_res.output
    assert "Spent: Rp 0" in today_res.output