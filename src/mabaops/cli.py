"""MabaOps command line interface."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text

from .assessor import DEFAULT_TIMEOUT_SECONDS, assess_solution, write_report
from .config import resolve_data_dir
from .models import CourseSchedule, TaskItem
from .storage import (
    add_budget_entry,
    add_schedule_item,
    add_task_item,
    budget_summary,
    delete_schedule_item,
    filter_schedule,
    indonesian_day_name,
    init_storage,
    load_app_data,
    load_schedule,
    load_tasks,
    normalize_day,
    plan_task_heuristic,
    set_weekly_budget,
    update_task_status,
)

app = typer.Typer(
    help="MabaOps: local-first command center for jadwal, tugas, and budget mahasiswa.",
    no_args_is_help=True,
)
schedule_app = typer.Typer(help="Manage jadwal kuliah.", no_args_is_help=True)
task_app = typer.Typer(help="Manage tugas dan deadline.", no_args_is_help=True)
budget_app = typer.Typer(help="Manage budget mingguan.", no_args_is_help=True)

app.add_typer(schedule_app, name="schedule")
app.add_typer(task_app, name="task")
app.add_typer(budget_app, name="budget")
console = Console()

DataDirOption = Annotated[
    str | None,
    typer.Option("--data-dir", help="Override local data directory. Defaults to ./data."),
]


@app.command()
def init(
    demo: Annotated[bool, typer.Option("--demo", help="Create demo data for screenshots and local trial.")] = False,
    data_dir: DataDirOption = None,
) -> None:
    """Initialize local MabaOps data files."""

    target_dir = resolve_data_dir(data_dir)
    written = init_storage(target_dir, demo=demo)

    console.print(f"[bold green]MabaOps siap.[/bold green] Data directory: {target_dir}")
    if written:
        console.print("File dibuat/diperbarui:")
        for path in written:
            console.print(f"- {path.name}")
    else:
        console.print("Data sudah ada. Tidak ada file yang ditimpa.")

    if demo:
        console.print("\nCoba lanjutkan dengan: [bold]mabaops today[/bold]")


@app.command()
def today(data_dir: DataDirOption = None) -> None:
    """Show today's schedule, nearest deadlines, and budget snapshot."""

    target_dir = resolve_data_dir(data_dir)
    if not target_dir.exists():
        console.print(Panel.fit(
            "Belum ada data MabaOps.\nMulai dengan: [bold]mabaops init --demo[/bold]",
            title="Perlu setup",
        ))
        raise typer.Exit(code=0)

    data = load_app_data(target_dir)
    today_name = indonesian_day_name(datetime.now().weekday())
    today_schedule = [item for item in data.schedule if item.day.lower() == today_name.lower()]
    open_tasks = [task for task in data.tasks if task.status != "done"][:3]
    summary = budget_summary(target_dir)
    spent = summary["spent"]
    remaining = summary["remaining"]
    weekly_budget = summary["weekly_budget"]

    table = Table(title=f"MabaOps Today - {today_name}", show_header=True, header_style="bold")
    table.add_column("Jadwal Hari Ini", overflow="fold")
    table.add_column("Deadline", overflow="fold")
    table.add_column("Budget", overflow="fold")

    schedule_lines = format_schedule_lines(today_schedule) or ["Belum ada jadwal hari ini."]
    task_lines = [f"[{task.urgency_label}] {task.due_date[:10]} - {task.title}" for task in open_tasks] or ["Belum ada tugas aktif."]
    budget_lines = [
        format_rupiah("Weekly", weekly_budget),
        format_rupiah("Spent", spent),
        format_rupiah("Left", remaining),
    ]

    max_rows = max(len(schedule_lines), len(task_lines), len(budget_lines))
    for index in range(max_rows):
        table.add_row(
            schedule_lines[index] if index < len(schedule_lines) else "",
            task_lines[index] if index < len(task_lines) else "",
            budget_lines[index] if index < len(budget_lines) else "",
        )

    console.print(table)
    console.print(f"\n[bold]Fokus:[/bold] {focus_message(bool(today_schedule), bool(open_tasks), remaining)}")


@app.command()
def dashboard(data_dir: DataDirOption = None) -> None:
    """Show the rich TUI dashboard (schedule, deadlines, budget, focus)."""

    target_dir = resolve_data_dir(data_dir)
    if not target_dir.exists():
        console.print(Panel.fit(
            "Belum ada data MabaOps.\nMulai dengan: [bold]mabaops init --demo[/bold]",
            title="Perlu setup",
        ))
        raise typer.Exit(code=0)

    data = load_app_data(target_dir)
    today_name = indonesian_day_name(datetime.now().weekday())
    today_schedule = [item for item in data.schedule if item.day.lower() == today_name.lower()]
    open_tasks = [task for task in data.tasks if task.status != "done"][:3]
    summary = budget_summary(target_dir)
    spent = summary["spent"]
    income = summary["income"]
    remaining = summary["remaining"]
    weekly_budget = summary["weekly_budget"]

    # Panel 1: Jadwal Hari Ini
    schedule_content = Text()
    if today_schedule:
        for item in today_schedule:
            schedule_content.append(f"{item.start_time}-{item.end_time}\n", style="bold cyan")
            schedule_content.append(f"{item.course_code} {item.course_name}\n")
            schedule_content.append(f"{location_text(item)}\n\n", style="dim")
    else:
        schedule_content.append("Belum ada jadwal hari ini.", style="dim")
    panel_schedule = Panel(schedule_content, title="Jadwal Hari Ini", border_style="cyan", expand=True)

    # Panel 2: Deadline Prioritas
    deadline_content = Text()
    if open_tasks:
        label_style = {"OVERDUE": "bold red", "URGENT": "bold yellow", "OK": "green", "DONE": "dim"}
        for task in open_tasks:
            style = label_style.get(task.urgency_label, "white")
            deadline_content.append(f"{task.urgency_label}", style=style)
            deadline_content.append(f" {task.due_date[:10]}\n")
            deadline_content.append(f"{task.title}\n\n", style="dim")
    else:
        deadline_content.append("Belum ada tugas aktif.", style="dim")
    panel_deadline = Panel(deadline_content, title="Deadline Prioritas", border_style="yellow", expand=True)

    # Panel 3: Budget
    budget_content = Text()
    if weekly_budget > 0:
        budget_content.append(f"{format_rupiah('Weekly', weekly_budget)}\n")
        budget_content.append(f"{format_rupiah('Spent', spent)}\n", style="red")
        budget_content.append(f"{format_rupiah('Left', remaining)}\n", style="green" if remaining >= 0 else "bold red")
        if weekly_budget + income > 0:
            used_ratio = min(1.0, max(0.0, spent / (weekly_budget + income)))
            filled = int(used_ratio * 10)
            bar = "#" * filled + "-" * (10 - filled)
            percent = int(used_ratio * 100)
            budget_content.append(f"\n{bar} {percent}%", style="red" if percent > 80 else "yellow" if percent > 50 else "green")
    else:
        budget_content.append("Budget belum diset.\n", style="dim")
        budget_content.append("budget set-weekly <amount>", style="cyan")
    panel_budget = Panel(budget_content, title="Budget", border_style="magenta", expand=True)

    header = Panel.fit(
        Text(f"Hari ini: {today_name}", style="bold", justify="center"),
        border_style="bright_blue",
    )

    console.print(header)
    console.print(Columns([panel_schedule, panel_deadline, panel_budget], expand=True))
    console.print(f"\n[bold]Fokus:[/bold] {focus_message(bool(today_schedule), bool(open_tasks), remaining)}")


# Schedule subcommands
@schedule_app.command("add")
def schedule_add(
    course_code: Annotated[str, typer.Option("--course-code", "-c", help="Kode mata kuliah, contoh: IF101.")],
    course_name: Annotated[str, typer.Option("--course-name", "-n", help="Nama mata kuliah.")],
    day: Annotated[str, typer.Option("--day", "-d", help="Hari kuliah, contoh: Senin.")],
    start_time: Annotated[str, typer.Option("--start", help="Jam mulai format HH:MM.")],
    end_time: Annotated[str, typer.Option("--end", help="Jam selesai format HH:MM.")],
    building: Annotated[str, typer.Option("--building", "-b", help="Gedung kelas.")] = "",
    room: Annotated[str, typer.Option("--room", "-r", help="Ruang kelas.")] = "",
    notes: Annotated[str, typer.Option("--notes", help="Catatan rute atau persiapan.")] = "",
    lecturer: Annotated[str, typer.Option("--lecturer", "-l", help="Nama dosen pengampu.")] = "",
    data_dir: DataDirOption = None,
) -> None:
    """Add a course schedule entry."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = add_schedule_item(
            target_dir,
            course_code=course_code,
            course_name=course_name,
            day=day,
            start_time=start_time,
            end_time=end_time,
            building=building,
            room=room,
            notes=notes,
            lecturer=lecturer,
        )
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print("[bold green]Jadwal ditambahkan.[/bold green]")
    console.print(f"{item.day} {item.start_time}-{item.end_time} | {item.course_code} {item.course_name} | {location_text(item)}")


@schedule_app.command("delete")
def schedule_delete(
    schedule_id: Annotated[str, typer.Argument(help="Kode MK (misal IF101) atau prefix ID jadwal yang akan dihapus.")],
    data_dir: DataDirOption = None,
) -> None:
    """Delete a course schedule entry."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = delete_schedule_item(target_dir, target_identifier=schedule_id)
    except ValueError as error:
        console.print(f"[bold red]Gagal menghapus jadwal:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Jadwal dihapus:[/bold green] {item.course_code} {item.course_name} ({item.day} {item.start_time}-{item.end_time})")


@schedule_app.command("list")
def schedule_list(
    day: Annotated[str | None, typer.Option("--day", "-d", help="Filter hari, contoh: Senin.")] = None,
    data_dir: DataDirOption = None,
) -> None:
    """List saved course schedules."""

    target_dir = resolve_data_dir(data_dir)
    try:
        schedule = filter_schedule(load_schedule(target_dir), day=day)
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    title = f"Jadwal Kuliah - {normalize_day(day)}" if day else "Jadwal Kuliah"
    print_schedule_table(schedule, title=title)


@schedule_app.command("today")
def schedule_today(data_dir: DataDirOption = None) -> None:
    """List today's course schedules."""

    today_name = indonesian_day_name(datetime.now().weekday())
    target_dir = resolve_data_dir(data_dir)
    schedule = filter_schedule(load_schedule(target_dir), day=today_name)
    print_schedule_table(schedule, title=f"Jadwal Hari Ini - {today_name}")


# Task subcommands
@task_app.command("add")
def task_add(
    title: Annotated[str, typer.Argument(help="Judul tugas.")],
    due: Annotated[str, typer.Option("--due", help="Deadline tugas (YYYY-MM-DD atau YYYY-MM-DD HH:MM).")],
    estimate: Annotated[int, typer.Option("--estimate", "-e", help="Estimasi waktu pengerjaan dalam menit.")] = 0,
    course: Annotated[str, typer.Option("--course", "-c", help="Kode mata kuliah terkait.")] = "",
    description: Annotated[str, typer.Option("--description", "-desc", help="Deskripsi detail tugas.")] = "",
    category: Annotated[str, typer.Option("--category", "-cat", help="Kategori tugas (coding, tugas, bacaan, lain-lain).")] = "coding",
    data_dir: DataDirOption = None,
) -> None:
    """Add a new task with priority scoring."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = add_task_item(
            target_dir,
            title=title,
            due_date=due,
            estimated_minutes=estimate,
            course_code=course,
            description=description,
            category=category,
        )
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Tugas ditambahkan (ID: {item.id[:8]})[/bold green]")
    console.print(f"[{item.urgency_label}] Due: {item.due_date} | {item.title} (Estimasi: {item.estimated_minutes}m)")


@task_app.command("plan")
def task_plan(
    task_id: Annotated[str, typer.Argument(help="ID atau prefix ID tugas yang ingin di-breakdown.")],
    data_dir: DataDirOption = None,
) -> None:
    """Breakdown a task into heuristic actionable micro-tasks (PRD 6.1 & 8.3)."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = plan_task_heuristic(target_dir, task_id_prefix=task_id)
    except ValueError as error:
        console.print(f"[bold red]Gagal membuat plan tugas:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Rencana pengerjaan (Actionable Micro-tasks):[/bold green] {item.title} (ID: {item.id[:8]})")
    for step in item.subtasks:
        console.print(f"  [bold cyan]->[/bold cyan] {step}")


@task_app.command("list")
def task_list(
    status: Annotated[str | None, typer.Option("--status", "-s", help="Filter status (pending, in_progress, done).")] = None,
    course: Annotated[str | None, typer.Option("--course", "-c", help="Filter kode mata kuliah.")] = None,
    data_dir: DataDirOption = None,
) -> None:
    """List tasks sorted by priority."""

    target_dir = resolve_data_dir(data_dir)
    tasks = load_tasks(target_dir)

    if status:
        tasks = [t for t in tasks if t.status.lower() == status.lower()]
    if course:
        tasks = [t for t in tasks if t.course_code.lower() == course.lower()]

    print_task_table(tasks, title="Daftar Tugas (Prioritas Tertinggi ke Terendah)")


@task_app.command("done")
def task_done(
    task_id: Annotated[str, typer.Argument(help="ID atau prefix ID tugas yang selesai.")],
    data_dir: DataDirOption = None,
) -> None:
    """Mark a task as completed (done)."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = update_task_status(target_dir, task_id_prefix=task_id, new_status="done")
    except ValueError as error:
        console.print(f"[bold red]Gagal memperbarui status:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Tugas selesai:[/bold green] {item.title} (ID: {item.id[:8]})")


@task_app.command("start")
def task_start(
    task_id: Annotated[str, typer.Argument(help="ID atau prefix ID tugas yang dikerjakan.")],
    data_dir: DataDirOption = None,
) -> None:
    """Mark a task as in_progress."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = update_task_status(target_dir, task_id_prefix=task_id, new_status="in_progress")
    except ValueError as error:
        console.print(f"[bold red]Gagal memperbarui status:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold cyan]Tugas dimulai (in_progress):[/bold cyan] {item.title} (ID: {item.id[:8]})")


@app.command()
def web(
    host: Annotated[str, typer.Option("--host", help="Host untuk bind server.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-p", help="Port server.")] = 8000,
) -> None:
    """Run the local web dashboard (full CRUD) at http://host:port."""

    try:
        from .web import main as web_main
    except ImportError as error:
        console.print("[bold red]Dependensi web belum terinstall.[/bold red]")
        console.print("Jalankan: [bold]pip install -e .[web][/bold]")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]MabaOps web jalan di:[/bold green] http://{host}:{port}")
    console.print("Ctrl+C untuk stop.")
    web_main(host=host, port=port)


@app.command()
def assess(
    solution: Annotated[Path, typer.Argument(help="Path file Python solusi tugas.", exists=True)],
    cases: Annotated[Path, typer.Option("--cases", "-c", help="Directory berisi pasangan .in/.out.")] = Path("test_cases"),
    timeout: Annotated[float, typer.Option("--timeout", "-t", help="Timeout per test case dalam detik.")] = DEFAULT_TIMEOUT_SECONDS,
    report_dir: Annotated[Path | None, typer.Option("--report-dir", help="Directory output report markdown.")] = None,
) -> None:
    """Run a Python solution against .in/.out test cases and write a report."""

    try:
        result = assess_solution(solution, cases, timeout=timeout)
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    status_style = {"passed": "green", "failed": "red", "timeout": "yellow", "error": "bold red"}
    table = Table(title=f"Assessment: {solution.name}", show_header=True, header_style="bold")
    table.add_column("Case")
    table.add_column("Status")
    table.add_column("Durasi", justify="right")
    table.add_column("Detail", overflow="fold")
    for case in result.cases:
        table.add_row(
            case.name,
            Text(case.status, style=status_style.get(case.status, "white")),
            f"{case.duration_ms}ms",
            case.detail or "-",
        )
    console.print(table)

    console.print(
        f"\n[bold]Skor:[/bold] {result.score} "
        f"({result.passed}/{result.total} passed, {result.failed} failed, {result.timeouts} timeout, {result.errors} error)"
    )

    reports_path = report_dir or Path("reports")
    report_path = write_report(result, reports_path, label=solution.stem)
    console.print(f"Report disimpan: [bold]{report_path}[/bold]")

    if result.passed < result.total:
        raise typer.Exit(code=1)


# Budget subcommands
@budget_app.command("set-weekly")
def budget_set_weekly(
    amount: Annotated[int, typer.Argument(help="Budget mingguan dalam Rupiah.")],
    data_dir: DataDirOption = None,
) -> None:
    """Set weekly budget amount."""

    target_dir = resolve_data_dir(data_dir)
    try:
        budget = set_weekly_budget(target_dir, amount)
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Budget mingguan diset:[/bold green] {format_rupiah('Total', budget.weekly_budget)}")


@budget_app.command("add")
def budget_add(
    entry_type: Annotated[str, typer.Argument(help="Tipe entri: expense atau income.")],
    amount: Annotated[int, typer.Argument(help="Jumlah dalam Rupiah.")],
    category: Annotated[str, typer.Option("--category", "-c", help="Kategori pengeluaran (makan, transport, print, organisasi, hiburan, lain-lain). Konsumsi income tidak memakai kategori.")] = "lain-lain",
    note: Annotated[str, typer.Option("--note", "-n", help="Catatan singkat.")] = "",
    data_dir: DataDirOption = None,
) -> None:
    """Add an expense or income entry."""

    target_dir = resolve_data_dir(data_dir)
    try:
        item = add_budget_entry(target_dir, entry_type=entry_type, amount=amount, category=category, note=note)
    except ValueError as error:
        console.print(f"[bold red]Input perlu diperbaiki:[/bold red] {error}")
        raise typer.Exit(code=1) from error

    label = "Pengeluaran" if item.type == "expense" else "Pemasukan"
    icon = "[bold red]-" if item.type == "expense" else "[bold green]+"
    console.print(f"[bold green]{label} dicatat.[/bold green] {icon}{format_rupiah('Rp', item.amount)}[/] | {item.category} | {item.note or '-'}")


@budget_app.command("summary")
def budget_summary_command(data_dir: DataDirOption = None) -> None:
    """Show weekly budget summary with spending pace warning."""

    target_dir = resolve_data_dir(data_dir)
    summary = budget_summary(target_dir)

    if summary["status"] == "no_budget":
        console.print(Panel.fit(
            "Budget mingguan belum diset.\nMulai dengan: [bold]mabaops budget set-weekly 500000[/bold]",
            title="Budget kosong",
        ))
        return

    table = Table(title="Ringkasan Budget Minggu Ini", show_header=False)
    table.add_column("Item", style="bold")
    table.add_column("Nilai", justify="right")
    table.add_row("Budget mingguan", format_rupiah("", summary["weekly_budget"]))
    table.add_row("Pemasukan (minggu ini)", format_rupiah("", summary["income"]))
    table.add_row("Pengeluaran (minggu ini)", format_rupiah("", summary["spent"]))
    table.add_row("Sisa", format_rupiah("", summary["remaining"]))
    table.add_row("Rata-rata per hari", format_rupiah("", summary["daily_pace"]))
    table.add_row("Proyeksi akhir minggu", format_rupiah("", summary["projected_end_of_week"]))
    table.add_row("Sisa hari di minggu ini", str(summary["days_left"]))
    console.print(table)

    status_messages = {
        "deficit": "[bold red]Perlu perhatian:[/bold red] pengeluaran sudah melebihi budget. Coba kurangi pengeluaran non-esensial.",
        "warning": "[yellow]Perlu perhatian:[/yellow] dengan pace saat ini, proyeksi akhir minggu melebihi budget.",
        "safe": "[bold green]Aman.[/bold green] Spending pace masih sesuai budget mingguan.",
    }
    console.print(f"\n{status_messages[summary['status']]}")


def print_task_table(tasks: list[TaskItem], title: str) -> None:
    if not tasks:
        console.print(Panel.fit(
            "Belum ada tugas.\nMulai dengan: [bold]mabaops task add[/bold]",
            title="Tugas kosong",
        ))
        return

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Status")
    table.add_column("Label")
    table.add_column("Deadline")
    table.add_column("MK", style="cyan")
    table.add_column("Judul Tugas", overflow="fold")
    table.add_column("Est", justify="right")
    table.add_column("Score", justify="right")

    for item in tasks:
        table.add_row(
            item.id[:8],
            item.status,
            item.urgency_label,
            item.due_date[:10],
            item.course_code or "-",
            item.title,
            f"{item.estimated_minutes}m",
            str(item.priority_score),
        )

    console.print(table)


def print_schedule_table(schedule: list[CourseSchedule], title: str) -> None:
    if not schedule:
        console.print(Panel.fit(
            "Belum ada jadwal.\nMulai dengan: [bold]mabaops schedule add[/bold]",
            title="Jadwal kosong",
        ))
        return

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Hari")
    table.add_column("Jam")
    table.add_column("Kode")
    table.add_column("Mata Kuliah", overflow="fold")
    table.add_column("Lokasi", overflow="fold")
    table.add_column("Catatan", overflow="fold")

    for item in schedule:
        table.add_row(
            item.day,
            f"{item.start_time}-{item.end_time}",
            item.course_code,
            item.course_name,
            location_text(item),
            item.notes or "-",
        )

    console.print(table)


def format_schedule_lines(schedule: list[CourseSchedule]) -> list[str]:
    return [
        f"{item.start_time} {item.course_name} ({location_text(item)})"
        for item in schedule
    ]


def location_text(item: CourseSchedule) -> str:
    if item.building and item.room:
        return f"{item.building} {item.room}"
    return item.room or item.building or "-"


def format_rupiah(label: str, amount: int) -> str:
    if label:
        return f"{label}: Rp {amount:,}".replace(",", ".")
    return f"Rp {amount:,}".replace(",", ".")


def focus_message(has_schedule: bool, has_tasks: bool, remaining_budget: int) -> str:
    if has_tasks:
        return "Kerjakan satu tugas prioritas selama 25-45 menit."
    if has_schedule:
        return "Siapkan kelas berikutnya dan review catatan singkat."
    if remaining_budget < 0:
        return "Budget perlu perhatian; cek pengeluaran minggu ini."
    return "Hari relatif aman. Tambahkan jadwal atau tugas kalau belum lengkap."


if __name__ == "__main__":
    app()