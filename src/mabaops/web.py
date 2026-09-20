"""Local web dashboard for MabaOps (FastAPI + Jinja2).

Full CRUD: kelola jadwal, tugas, dan budget dari browser.
Data tetap local-first di file JSON yang sama dengan CLI.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .config import resolve_data_dir
from .storage import (
    add_budget_entry,
    add_schedule_item,
    add_task_item,
    budget_summary,
    delete_budget_entry,
    delete_schedule_item,
    delete_task_item,
    indonesian_day_name,
    load_app_data,
    load_budget_entries,
    load_schedule,
    load_tasks,
    normalize_day,
    set_weekly_budget,
    update_task_status,
)

app = FastAPI(title="MabaOps Web", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _fmt_rupiah(amount: int) -> str:
    return f"Rp {amount:,}".replace(",", ".")


def _context(data_dir: Path) -> dict:
    data = load_app_data(data_dir)
    today_name = indonesian_day_name(datetime.now().weekday())
    today_schedule = [s for s in data.schedule if s.day.lower() == today_name.lower()]
    open_tasks = [t for t in data.tasks if t.status != "done"]
    summary = budget_summary(data_dir)
    return {
        "today_name": today_name,
        "schedule": data.schedule,
        "today_schedule": today_schedule,
        "tasks": data.tasks,
        "open_tasks": open_tasks,
        "budget_entries": list(reversed(load_budget_entries(data_dir))),
        "summary": summary,
        "fmt": _fmt_rupiah,
        "data_dir": str(data_dir),
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    data_dir = resolve_data_dir(None)
    if not data_dir.exists():
        return templates.TemplateResponse(request, "setup.html", {})
    return templates.TemplateResponse(request, "index.html", _context(data_dir))


# ---- Schedule ----
@app.post("/schedule/add")
def schedule_add(
    course_code: str = Form(...),
    course_name: str = Form(...),
    day: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    building: str = Form(""),
    room: str = Form(""),
    notes: str = Form(""),
):
    data_dir = resolve_data_dir(None)
    try:
        add_schedule_item(
            data_dir,
            course_code=course_code.strip(),
            course_name=course_name.strip(),
            day=day,
            start_time=start_time.strip(),
            end_time=end_time.strip(),
            building=building.strip(),
            room=room.strip(),
            notes=notes.strip(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


@app.post("/schedule/{schedule_id}/delete")
def schedule_delete(schedule_id: str):
    data_dir = resolve_data_dir(None)
    try:
        delete_schedule_item(data_dir, target_identifier=schedule_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


# ---- Tasks ----
@app.post("/task/add")
def task_add(
    title: str = Form(...),
    due: str = Form(...),
    estimate: int = Form(0),
    course: str = Form(""),
):
    data_dir = resolve_data_dir(None)
    try:
        add_task_item(
            data_dir,
            title=title.strip(),
            due_date=due.strip(),
            estimated_minutes=estimate,
            course_code=course.strip(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


@app.post("/task/{task_id}/status")
def task_status(task_id: str, status: str = Form(...)):
    data_dir = resolve_data_dir(None)
    if status not in ("pending", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Status tidak valid.")
    try:
        update_task_status(data_dir, task_id_prefix=task_id, new_status=status)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


@app.post("/task/{task_id}/delete")
def task_delete(task_id: str):
    data_dir = resolve_data_dir(None)
    try:
        delete_task_item(data_dir, task_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


# ---- Budget ----
@app.post("/budget/set-weekly")
def budget_set_weekly(amount: int = Form(...)):
    data_dir = resolve_data_dir(None)
    try:
        set_weekly_budget(data_dir, amount)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


@app.post("/budget/add")
def budget_add(
    entry_type: str = Form(...),
    amount: int = Form(...),
    category: str = Form("lain-lain"),
    note: str = Form(""),
):
    data_dir = resolve_data_dir(None)
    try:
        add_budget_entry(
            data_dir,
            entry_type=entry_type,
            amount=amount,
            category=category,
            note=note.strip(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


@app.post("/budget/{entry_id}/delete")
def budget_delete(entry_id: str):
    data_dir = resolve_data_dir(None)
    try:
        delete_budget_entry(data_dir, entry_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RedirectResponse("/", status_code=303)


def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")
