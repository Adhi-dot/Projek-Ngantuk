"""Local JSON storage for MabaOps."""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from .models import AppData, BudgetConfig, BudgetEntry, CourseSchedule, TaskItem

SCHEDULE_FILE = "schedule.json"
TASKS_FILE = "tasks.json"
BUDGET_FILE = "budget.json"
BUDGET_ENTRIES_FILE = "budget_entries.json"

VALID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def ensure_data_dir(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: object) -> None:
    ensure_data_dir(path.parent)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    # Windows retry loop for atomic replace under file lock
    for attempt in range(5):
        try:
            temp_path.replace(path)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)


def init_storage(data_dir: Path, demo: bool = False) -> list[Path]:
    ensure_data_dir(data_dir)
    payloads = demo_payloads() if demo else empty_payloads()
    written: list[Path] = []
    for filename, payload in payloads.items():
        target = data_dir / filename
        if not target.exists() or demo:
            write_json(target, payload)
            written.append(target)
    return written


def empty_payloads() -> dict[str, object]:
    return {
        SCHEDULE_FILE: [],
        TASKS_FILE: [],
        BUDGET_FILE: {"weekly_budget": 0, "currency": "IDR"},
        BUDGET_ENTRIES_FILE: [],
    }


def demo_payloads() -> dict[str, object]:
    today_name = indonesian_day_name(datetime.now().weekday())
    now = datetime.now()
    due_soon = (now + timedelta(days=1)).strftime("%Y-%m-%dT23:59:00")
    due_later = (now + timedelta(days=5)).strftime("%Y-%m-%dT23:59:00")
    return {
        SCHEDULE_FILE: [
            {
                "id": str(uuid4()),
                "course_code": "IF101",
                "course_name": "Algoritma dan Pemrograman",
                "day": today_name,
                "start_time": "08:00",
                "end_time": "10:30",
                "building": "Gedung A",
                "room": "A201",
                "notes": "Datang 10 menit lebih awal.",
            },
            {
                "id": str(uuid4()),
                "course_code": "MA101",
                "course_name": "Kalkulus Dasar",
                "day": today_name,
                "start_time": "13:00",
                "end_time": "14:40",
                "building": "Gedung B",
                "room": "B104",
                "notes": "Bawa buku latihan.",
            },
        ],
        TASKS_FILE: [
            {
                "id": str(uuid4()),
                "title": "Tugas Array",
                "due_date": due_soon,
                "estimated_minutes": 120,
                "status": "pending",
                "course_code": "IF101",
            },
            {
                "id": str(uuid4()),
                "title": "Resume Materi PKKMB",
                "due_date": due_later,
                "estimated_minutes": 45,
                "status": "pending",
                "course_code": "UM101",
            },
        ],
        BUDGET_FILE: {"weekly_budget": 500000, "currency": "IDR"},
        BUDGET_ENTRIES_FILE: [
            {
                "id": str(uuid4()),
                "type": "expense",
                "amount": 15000,
                "category": "makan",
                "note": "Nasi ayam kantin",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        ],
    }


def load_app_data(data_dir: Path) -> AppData:
    raw_schedule = read_json(data_dir / SCHEDULE_FILE, [])
    raw_tasks = read_json(data_dir / TASKS_FILE, [])
    budget = read_json(data_dir / BUDGET_FILE, {"weekly_budget": 0, "currency": "IDR"})
    budget_entries = read_json(data_dir / BUDGET_ENTRIES_FILE, [])

    schedule = [CourseSchedule.model_validate(item) for item in raw_schedule]
    tasks = [enrich_task_item(TaskItem.model_validate(item)) for item in raw_tasks]
    tasks.sort(key=lambda t: t.priority_score, reverse=True)

    raw = {
        "schedule": [s.model_dump() for s in schedule],
        "tasks": [t.model_dump() for t in tasks],
        "budget": budget,
        "budget_entries": budget_entries,
    }
    return AppData.model_validate(raw)


def load_schedule(data_dir: Path) -> list[CourseSchedule]:
    raw_items = read_json(data_dir / SCHEDULE_FILE, [])
    return [CourseSchedule.model_validate(item) for item in raw_items]


def save_schedule(data_dir: Path, schedule: list[CourseSchedule]) -> None:
    write_json(data_dir / SCHEDULE_FILE, [item.model_dump() for item in schedule])


def add_schedule_item(
    data_dir: Path,
    course_code: str,
    course_name: str,
    day: str,
    start_time: str,
    end_time: str,
    building: str = "",
    room: str = "",
    notes: str = "",
    lecturer: str = "",
) -> CourseSchedule:
    ensure_data_dir(data_dir)
    schedule = load_schedule(data_dir)
    item = CourseSchedule(
        id=str(uuid4()),
        course_code=course_code,
        course_name=course_name,
        day=normalize_day(day),
        start_time=start_time,
        end_time=end_time,
        building=building,
        room=room,
        notes=notes,
        lecturer=lecturer,
    )
    schedule.append(item)
    schedule.sort(key=lambda entry: (day_index(entry.day), entry.start_time, entry.course_name))
    save_schedule(data_dir, schedule)
    return item


def delete_schedule_item(data_dir: Path, target_identifier: str) -> CourseSchedule:
    schedule = load_schedule(data_dir)
    matched_idx = -1
    for idx, entry in enumerate(schedule):
        if entry.id.startswith(target_identifier) or entry.course_code.lower() == target_identifier.lower():
            matched_idx = idx
            break
    if matched_idx == -1:
        raise ValueError(f"Jadwal dengan kode atau ID '{target_identifier}' tidak ditemukan.")
    deleted = schedule.pop(matched_idx)
    save_schedule(data_dir, schedule)
    return deleted


def delete_schedule_item(data_dir: Path, target_identifier: str | None = None, schedule_id: str | None = None) -> CourseSchedule:
    """Delete a schedule entry.

    Matched by (in order): exact id, id prefix, or exact course_code.
    Raises ValueError when zero or multiple entries match.
    """

    key = (target_identifier or schedule_id or "").strip()
    schedule = load_schedule(data_dir)
    matches = [
        item for item in schedule
        if item.id == key
        or item.id.startswith(key)
        or item.course_code.lower() == key.lower()
    ]
    if not matches:
        raise ValueError(f"Jadwal dengan ID/kode '{key[:8]}' tidak ditemukan.")
    if len(matches) > 1:
        raise ValueError(f"'{key}' cocok dengan {len(matches)} jadwal. Gunakan ID yang lebih spesifik.")
    matched = matches[0]
    schedule = [item for item in schedule if item.id != matched.id]
    save_schedule(data_dir, schedule)
    return matched


def filter_schedule(schedule: list[CourseSchedule], day: str | None = None) -> list[CourseSchedule]:
    if day is None:
        return sorted(schedule, key=lambda entry: (day_index(entry.day), entry.start_time, entry.course_name))
    normalized = normalize_day(day)
    return sorted(
        [item for item in schedule if item.day.lower() == normalized.lower()],
        key=lambda entry: (entry.start_time, entry.course_name),
    )


def load_tasks(data_dir: Path) -> list[TaskItem]:
    raw_items = read_json(data_dir / TASKS_FILE, [])
    tasks = [enrich_task_item(TaskItem.model_validate(item)) for item in raw_items]
    tasks.sort(key=lambda t: t.priority_score, reverse=True)
    return tasks


def save_tasks(data_dir: Path, tasks: list[TaskItem]) -> None:
    write_json(data_dir / TASKS_FILE, [item.model_dump() for item in tasks])


def add_task_item(
    data_dir: Path,
    title: str,
    due_date: str,
    estimated_minutes: int = 0,
    course_code: str = "",
    description: str = "",
    category: str = "coding",
) -> TaskItem:
    ensure_data_dir(data_dir)
    parsed_due = parse_due_date(due_date)
    tasks = load_tasks(data_dir)
    item = TaskItem(
        id=str(uuid4()),
        title=title,
        due_date=parsed_due,
        estimated_minutes=estimated_minutes,
        status="pending",
        course_code=course_code,
        description=description,
        category=category,
    )
    item = enrich_task_item(item)
    tasks.append(item)
    tasks.sort(key=lambda t: t.priority_score, reverse=True)
    save_tasks(data_dir, tasks)
    return item


def plan_task_heuristic(data_dir: Path, task_id_prefix: str) -> TaskItem:
    """Breakdown a task into heuristic micro-tasks (PRD 6.1 & 8.3)."""
    tasks = load_tasks(data_dir)
    matched: TaskItem | None = None
    for task in tasks:
        if task.id.startswith(task_id_prefix):
            matched = task
            break
    if not matched:
        raise ValueError(f"Task dengan ID atau prefix '{task_id_prefix}' tidak ditemukan.")

    if matched.category.lower() == "coding" or "coding" in matched.title.lower() or "tugas" in matched.title.lower():
        subtasks = [
            "1. Pahami soal & analisis test cases (15m)",
            "2. Implementasi struktur data & logika utama (45m)",
            "3. Uji edge cases & running test (.in/.out) (30m)",
            "4. Refactor kode & periksa rubrik pengumpulan (15m)",
        ]
    else:
        subtasks = [
            "1. Kumpulkan bahan bacaan & buat kerangka garis besar (20m)",
            "2. Kerjakan bagian inti secara fokus (45m)",
            "3. Review akhir, periksa format & submit (15m)",
        ]

    matched.subtasks = subtasks
    matched = enrich_task_item(matched)
    tasks.sort(key=lambda t: t.priority_score, reverse=True)
    save_tasks(data_dir, tasks)
    return matched


def delete_task_item(data_dir: Path, task_id: str) -> TaskItem:
    """Delete a task by exact id. Returns the removed item."""

    tasks = load_tasks(data_dir)
    matched = next((item for item in tasks if item.id == task_id), None)
    if not matched:
        raise ValueError(f"Task dengan ID '{task_id[:8]}' tidak ditemukan.")
    tasks = [item for item in tasks if item.id != task_id]
    save_tasks(data_dir, tasks)
    return matched


def update_task_status(data_dir: Path, task_id_prefix: str, new_status: str) -> TaskItem:
    tasks = load_tasks(data_dir)
    matched: TaskItem | None = None
    for task in tasks:
        if task.id.startswith(task_id_prefix):
            matched = task
            break
    if not matched:
        raise ValueError(f"Task dengan ID atau prefix '{task_id_prefix}' tidak ditemukan.")
    matched.status = new_status
    matched = enrich_task_item(matched)
    tasks.sort(key=lambda t: t.priority_score, reverse=True)
    save_tasks(data_dir, tasks)
    return matched


def parse_due_date(raw_due: str) -> str:
    cleaned = raw_due.strip()
    # Try parsing common formats
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            if "T" not in cleaned and " " not in cleaned:
                dt = dt.replace(hour=23, minute=59, second=0)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    raise ValueError(f"Format deadline tidak valid: '{raw_due}'. Gunakan YYYY-MM-DD atau YYYY-MM-DD HH:MM.")


def enrich_task_item(item: TaskItem) -> TaskItem:
    if item.status == "done":
        item.priority_score = -1
        item.urgency_label = "DONE"
        return item

    try:
        due_dt = datetime.strptime(item.due_date[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        item.priority_score = 0
        item.urgency_label = "OK"
        return item

    now = datetime.now()
    delta = due_dt - now
    hours_left = delta.total_seconds() / 3600.0

    if hours_left < 0:
        item.urgency_label = "OVERDUE"
        # Overdue tasks get highest score, scaled by how overdue
        overdue_hours = abs(hours_left)
        item.priority_score = 1000 + int(overdue_hours)
    elif hours_left <= 48:
        item.urgency_label = "URGENT"
        # Urgent tasks due within 48 hours: base 500 + closeness bonus
        closeness = max(0, int((48 - hours_left) * 10))
        estimate_bonus = min(50, item.estimated_minutes // 5)
        item.priority_score = 500 + closeness + estimate_bonus
    else:
        item.urgency_label = "OK"
        days_left = hours_left / 24.0
        # Normal priority: closer due date and larger estimation gives higher priority
        time_score = max(0, int((30 - min(days_left, 30)) * 10))
        estimate_bonus = min(30, item.estimated_minutes // 10)
        item.priority_score = 100 + time_score + estimate_bonus

    return item


def normalize_day(day: str) -> str:
    cleaned = day.strip().lower()
    aliases = {
        "senin": "Senin",
        "selasa": "Selasa",
        "rabu": "Rabu",
        "kamis": "Kamis",
        "jumat": "Jumat",
        "jum'at": "Jumat",
        "jum’at": "Jumat",
        "sabtu": "Sabtu",
        "minggu": "Minggu",
        "ahad": "Minggu",
    }
    if cleaned not in aliases:
        valid = ", ".join(VALID_DAYS)
        raise ValueError(f"Hari tidak valid: {day}. Contoh hari: {valid}.")
    return aliases[cleaned]


def day_index(day: str) -> int:
    try:
        return VALID_DAYS.index(normalize_day(day))
    except ValueError:
        return len(VALID_DAYS)


def indonesian_day_name(weekday: int) -> str:
    return VALID_DAYS[weekday]


# Budget management
EXPENSE_CATEGORIES = ["makan", "transport", "print", "organisasi", "hiburan", "lain-lain"]


def load_budget(data_dir: Path) -> BudgetConfig:
    raw = read_json(data_dir / BUDGET_FILE, {"weekly_budget": 0, "currency": "IDR"})
    return BudgetConfig.model_validate(raw)


def save_budget(data_dir: Path, budget: BudgetConfig) -> None:
    write_json(data_dir / BUDGET_FILE, budget.model_dump())


def set_weekly_budget(data_dir: Path, weekly_budget: int) -> BudgetConfig:
    if weekly_budget < 0:
        raise ValueError("Weekly budget tidak boleh negatif.")
    ensure_data_dir(data_dir)
    budget = load_budget(data_dir)
    budget.weekly_budget = weekly_budget
    save_budget(data_dir, budget)
    return budget


def load_budget_entries(data_dir: Path) -> list[BudgetEntry]:
    raw_items = read_json(data_dir / BUDGET_ENTRIES_FILE, [])
    return [BudgetEntry.model_validate(item) for item in raw_items]


def save_budget_entries(data_dir: Path, entries: list[BudgetEntry]) -> None:
    write_json(data_dir / BUDGET_ENTRIES_FILE, [item.model_dump() for item in entries])


def normalize_category(category: str) -> str:
    cleaned = category.strip().lower()
    aliases = {
        "makan": "makan",
        "minum": "makan",
        "transport": "transport",
        "transportasi": "transport",
        "gojek": "transport",
        "print": "print",
        "fotokopi": "print",
        "print/fotokopi": "print",
        "organisasi": "organisasi",
        "hiburan": "hiburan",
        "lain": "lain-lain",
        "lain-lain": "lain-lain",
    }
    if cleaned not in aliases:
        valid = ", ".join(EXPENSE_CATEGORIES)
        raise ValueError(f"Kategori tidak valid: {category}. Kategori tersedia: {valid}.")
    return aliases[cleaned]


def add_budget_entry(
    data_dir: Path,
    entry_type: str,
    amount: int,
    category: str = "lain-lain",
    note: str = "",
) -> BudgetEntry:
    if entry_type not in ("expense", "income"):
        raise ValueError(f"Tipe entri tidak valid: {entry_type}. Gunakan 'expense' atau 'income'.")
    if amount <= 0:
        raise ValueError("Jumlah harus lebih besar dari 0.")
    ensure_data_dir(data_dir)
    item = BudgetEntry(
        id=str(uuid4()),
        type=entry_type,
        amount=amount,
        category=normalize_category(category) if entry_type == "expense" else "lain-lain",
        note=note,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    entries = load_budget_entries(data_dir)
    entries.append(item)
    save_budget_entries(data_dir, entries)
    return item


def delete_budget_entry(data_dir: Path, entry_id: str) -> BudgetEntry:
    """Delete a budget entry by exact id. Returns the removed item."""

    entries = load_budget_entries(data_dir)
    matched = next((item for item in entries if item.id == entry_id), None)
    if not matched:
        raise ValueError(f"Entri budget dengan ID '{entry_id[:8]}' tidak ditemukan.")
    entries = [item for item in entries if item.id != entry_id]
    save_budget_entries(data_dir, entries)
    return matched


def budget_summary(data_dir: Path, now: datetime | None = None) -> dict:
    """Compute weekly budget summary and spending pace warning.

    Warning logic: compare spending pace against the remaining days of the week.
    Week starts Monday (consistent with schedule). If projected end-of-week spend
    exceeds the weekly budget, mark warning.
    """

    now = now or datetime.now()
    budget = load_budget(data_dir)
    entries = load_budget_entries(data_dir)

    # Only consider entries created during the current week (Monday as day 1)
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    next_monday = monday + timedelta(days=7)
    week_entries = []
    for entry in entries:
        try:
            entry_dt = datetime.fromisoformat(entry.created_at)
            if monday <= entry_dt < next_monday:
                week_entries.append(entry)
        except (ValueError, TypeError):
            continue

    spent = sum(entry.amount for entry in week_entries if entry.type == "expense")
    income = sum(entry.amount for entry in week_entries if entry.type == "income")
    remaining = budget.weekly_budget + income - spent

    days_elapsed = max(1, now.weekday() + 1)  # Senin=1 ... Minggu=7
    days_left = max(0, 7 - days_elapsed)
    daily_pace = spent / days_elapsed
    projected_end_of_week = int(daily_pace * 7)
    over_budget = budget.weekly_budget > 0 and projected_end_of_week > budget.weekly_budget

    if budget.weekly_budget <= 0:
        status = "no_budget"
    elif remaining < 0:
        status = "deficit"
    elif over_budget:
        status = "warning"
    else:
        status = "safe"

    return {
        "weekly_budget": budget.weekly_budget,
        "income": income,
        "spent": spent,
        "remaining": remaining,
        "daily_pace": int(daily_pace),
        "projected_end_of_week": projected_end_of_week,
        "days_left": days_left,
        "status": status,
    }