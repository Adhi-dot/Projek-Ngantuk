# MabaOps Roadmap

## MVP (Selesai)

- [x] **Milestone 1 — Foundation:** Package skeleton, `init`, `init --demo`, JSON storage, config resolution.
- [x] **Milestone 2 — Schedule + Today:** `schedule add/list/today`, normalisasi hari, `today` dashboard.
- [x] **Milestone 3 — Tasks + Priority:** `task add/list/start/done`, priority score (OVERDUE/URGENT/OK), integrasi top-3 di `today`.
- [x] **Milestone 4 — Budget:** `budget set-weekly/add/summary`, kategori expense, spending pace warning (safe/warning/deficit).
- [x] **Milestone 5 — TUI Dashboard:** `dashboard` Rich 3-panel layout + progress bar budget + saran fokus.
- [x] **Milestone 6 — Code Assessor:** `assess file.py --cases dir`, timeout protection, skor, markdown report di `reports/`.
- [x] **Web Dashboard (local):** `mabaops web` — full CRUD jadwal/tugas/budget dari browser di localhost (FastAPI + Jinja2), data sinkron dengan CLI.

## Post-MVP

- [ ] **Notes-to-Quiz:** Generate kuis dari catatan markdown (`mabaops quiz`).
- [ ] **Material summarizer:** Ringkas PDF/materi kuliah.
- [ ] **OCR import:** Import jadwal/catatan dari foto.
- [ ] **Export jadwal `.ics`:** Sinkron dengan Google Calendar.
- [ ] **Weekly review generator:** `mabaops review-week` (tugas selesai/missed, budget risk).
- [x] **Schedule delete:** `mabaops schedule delete <code|id>`.
- [x] **Task breakdown heuristik:** Pecah tugas besar jadi micro-tasks otomatis (`mabaops task plan <id>`).
- [ ] **Schedule edit:** `mabaops schedule edit <id>`.
- [ ] **SQLite migration:** Upgrade dari JSON jika data membesar.
- [ ] **Textual TUI:** Dashboard interaktif penuh menggantikan Rich static.
- [ ] **AI-assisted features (optional):** Fallback heuristic tetap jalan tanpa API key.

## Ide Lain

- Plugin/skill MabaOps untuk Claude Code (`.claude/commands`).
- ~~Web dashboard read-only~~ → ✅ sudah jadi full CRUD di MVP (mabaops web).
- Import schedule dari CSV/JSON template kampus.
