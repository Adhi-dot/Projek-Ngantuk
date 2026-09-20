"""Tests for the MabaOps web dashboard (FastAPI)."""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from mabaops.web import app

client = TestClient(app, follow_redirects=False)


def _init_data_dir(tmp_path):
    data_dir = tmp_path / "webdata"
    data_dir.mkdir()
    import json

    for name, payload in [
        ("schedule.json", []),
        ("tasks.json", []),
        ("budget.json", {"weekly_budget": 0, "currency": "IDR"}),
        ("budget_entries.json", []),
    ]:
        (data_dir / name).write_text(json.dumps(payload), encoding="utf-8")
    return data_dir


def test_index_requires_init(monkeypatch, tmp_path):
    monkeypatch.setenv("MABAOPS_DATA_DIR", str(tmp_path / "missing"))
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Perlu Setup" in resp.text or "Belum ada data" in resp.text


def test_full_schedule_crud(monkeypatch, tmp_path):
    monkeypatch.setenv("MABAOPS_DATA_DIR", str(_init_data_dir(tmp_path)))

    # Create
    resp = client.post(
        "/schedule/add",
        data={"course_code": "IF101", "course_name": "Algoritma", "day": "Senin",
              "start_time": "08:00", "end_time": "10:30"},
    )
    assert resp.status_code == 303

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Algoritma" in resp.text

    # Invalid day rejected
    resp = client.post(
        "/schedule/add",
        data={"course_code": "IF1", "course_name": "X", "day": "Funday",
              "start_time": "08:00", "end_time": "09:00"},
    )
    assert resp.status_code == 400

    # Delete
    from mabaops.storage import load_schedule
    item = load_schedule(Path(os.environ["MABAOPS_DATA_DIR"]))[0]
    resp = client.post(f"/schedule/{item.id}/delete")
    assert resp.status_code == 303
    assert load_schedule(Path(os.environ["MABAOPS_DATA_DIR"])) == []


def test_full_task_crud(monkeypatch, tmp_path):
    data_dir = _init_data_dir(tmp_path)
    monkeypatch.setenv("MABAOPS_DATA_DIR", str(data_dir))

    resp = client.post(
        "/task/add",
        data={"title": "Tugas Web", "due": "2026-09-30", "estimate": "60", "course": "IF102"},
    )
    assert resp.status_code == 303

    from pathlib import Path
    from mabaops.storage import load_tasks
    tasks = load_tasks(data_dir)
    assert tasks[0].title == "Tugas Web"

    # Start then done
    resp = client.post(f"/task/{tasks[0].id}/status", data={"status": "in_progress"})
    assert resp.status_code == 303
    assert load_tasks(data_dir)[0].status == "in_progress"

    resp = client.post(f"/task/{tasks[0].id}/status", data={"status": "done"})
    assert resp.status_code == 303
    assert load_tasks(data_dir)[0].status == "done"

    # Invalid status rejected
    resp = client.post(f"/task/{tasks[0].id}/status", data={"status": "selesai"})
    assert resp.status_code == 400

    # Delete
    resp = client.post(f"/task/{tasks[0].id}/delete")
    assert resp.status_code == 303
    assert load_tasks(data_dir) == []


def test_full_budget_crud(monkeypatch, tmp_path):
    data_dir = _init_data_dir(tmp_path)
    monkeypatch.setenv("MABAOPS_DATA_DIR", str(data_dir))

    resp = client.post("/budget/set-weekly", data={"amount": "500000"})
    assert resp.status_code == 303

    resp = client.post(
        "/budget/add",
        data={"entry_type": "expense", "amount": "15000", "category": "makan", "note": "ayam"},
    )
    assert resp.status_code == 303

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Rp 500.000" in resp.text
    assert "ayam" in resp.text

    # Invalid category rejected
    resp = client.post(
        "/budget/add",
        data={"entry_type": "expense", "amount": "1000", "category": "kuliner"},
    )
    assert resp.status_code == 400

    # Delete entry
    from pathlib import Path
    from mabaops.storage import load_budget_entries
    entry = load_budget_entries(data_dir)[0]
    resp = client.post(f"/budget/{entry.id}/delete")
    assert resp.status_code == 303
    assert load_budget_entries(data_dir) == []
