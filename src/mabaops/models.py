"""Pydantic data models for MabaOps."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CourseSchedule(BaseModel):
    id: str
    course_code: str
    course_name: str
    day: str
    start_time: str
    end_time: str
    building: str = ""
    room: str = ""
    notes: str = ""
    lecturer: str = ""


class TaskItem(BaseModel):
    id: str
    title: str
    due_date: str
    estimated_minutes: int = 0
    status: str = "pending"
    course_code: str = ""
    description: str = ""
    category: str = "coding"
    priority_score: int = 0
    urgency_label: str = "OK"
    subtasks: list[str] = Field(default_factory=list)


class BudgetConfig(BaseModel):
    weekly_budget: int = 0
    currency: str = "IDR"


class BudgetEntry(BaseModel):
    id: str
    type: str
    amount: int
    category: str = "lain-lain"
    note: str = ""
    created_at: str


class AssessmentReport(BaseModel):
    id: str
    target_file: str
    cases_dir: str
    passed: int = 0
    failed: int = 0
    timeouts: int = 0
    errors: int = 0
    score: int = 0
    report_path: str = ""
    created_at: str = ""


class AppData(BaseModel):
    schedule: list[CourseSchedule] = Field(default_factory=list)
    tasks: list[TaskItem] = Field(default_factory=list)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    budget_entries: list[BudgetEntry] = Field(default_factory=list)