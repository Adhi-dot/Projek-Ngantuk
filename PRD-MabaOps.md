# PRD: MabaOps

> **Student life operating system for Indonesian college freshmen.**  
> Local-first command center for jadwal kuliah, tugas, budget, catatan belajar, dan workflow mingguan mahasiswa.

---

## 1. Executive Summary

**MabaOps** adalah aplikasi CLI/TUI local-first untuk membantu mahasiswa baru mengelola kehidupan kampus secara praktis: jadwal kuliah, deadline tugas, budget mingguan, catatan belajar, dan evaluasi tugas coding. Produk ini dirancang sebagai flagship GitHub project yang memanfaatkan kekuatan environment Claude Code pengguna: worktree-based development, skills/plugins, RTK output compression, AI-assisted planning, dan agentic workflow.

MabaOps bukan sekadar todo app. Positioning utamanya adalah **student operations system**: satu tempat untuk melihat “apa yang harus saya lakukan hari ini?”, “deadline mana yang bahaya?”, “uang minggu ini cukup nggak?”, dan “apa langkah belajar paling kecil yang bisa saya kerjakan sekarang?”.

Target awal adalah mahasiswa Indonesia, terutama maba Informatika/teknik/komputer yang mulai kewalahan dengan transisi SMA → kuliah.

---

## 2. Product Goals

### 2.1 Goals

1. Membantu mahasiswa baru mengambil keputusan harian dengan cepat.
2. Menggabungkan jadwal, tugas, budget, dan catatan belajar dalam satu command center.
3. Menyediakan workflow local-first yang tetap bisa berjalan tanpa cloud.
4. Menjadikan repo GitHub yang rapi, demo-able, dan portfolio-worthy.
5. Mengintegrasikan ulang kekuatan project sebelumnya: CampusNav, Budget Tracker, Personal Code Assessor, dan study tools.

### 2.2 Non-Goals untuk MVP

1. Bukan LMS penuh seperti Google Classroom/Moodle.
2. Bukan aplikasi mobile native.
3. Bukan replacement kalender resmi kampus.
4. Bukan financial accounting lengkap.
5. Bukan AI chatbot bebas tanpa struktur.
6. Bukan cloud SaaS multi-user pada fase pertama.

---

## 3. Problem Statement

Mahasiswa baru sering punya banyak konteks yang tersebar:

- Jadwal kuliah ada di screenshot, PDF, chat grup, atau portal kampus.
- Deadline tugas ada di WhatsApp, catatan, LMS, atau ingatan.
- Pengeluaran harian jarang tercatat sampai uang menipis.
- Catatan kuliah tercecer dalam file markdown, PDF, foto papan tulis, atau notebook.
- Tugas coding sulit dievaluasi sebelum dikumpulkan.

Masalah utamanya bukan hanya “kurang produktif”, tapi **kurang visibility**. Mahasiswa butuh dashboard sederhana yang menjawab:

> “Hari ini apa yang paling penting, berapa waktu saya punya, dan apa langkah kecil berikutnya?”

---

## 4. Target Users

### 4.1 Primary Persona: Maba Informatika

**Nama persona:** Adhi, mahasiswa baru Informatika  
**Kondisi:** Baru masuk kuliah, mulai banyak tugas coding, jadwal berubah-ubah, ingin punya portfolio GitHub.  
**Pain points:**

- Susah prioritas deadline.
- Tugas coding sering baru ketahuan error saat mepet.
- Budget makan/transport bocor tanpa sadar.
- Catatan kuliah tidak terstruktur.
- Butuh project GitHub yang keren dan relevan.

### 4.2 Secondary Persona: Mahasiswa Umum

Mahasiswa non-teknik yang butuh planner lokal sederhana untuk jadwal, tugas, dan budget tanpa fitur coding-assessor.

### 4.3 Tertiary Persona: Mentor/Kakak Tingkat

Kakak tingkat atau mentor yang ingin memberikan template workflow belajar ke junior.

---

## 5. Value Proposition

MabaOps memberi mahasiswa satu command center yang:

1. **Cepat:** `mabaops today` langsung menampilkan jadwal, deadline, budget, dan rekomendasi fokus.
2. **Local-first:** Data tersimpan lokal; tidak wajib login.
3. **Mahasiswa-native:** Kategori dan bahasa sesuai realita kampus Indonesia.
4. **GitHub-worthy:** CLI/TUI dengan screenshot keren, docs rapi, dan struktur engineering jelas.
5. **Claude Code-native:** Mudah dikembangkan dengan custom commands, PRD, roadmap, dan agent workflow.

---

## 6. Product Scope

### 6.1 MVP Scope

MVP harus punya 5 modul inti:

1. **Today Dashboard**
   - Menampilkan kelas hari ini.
   - Menampilkan deadline terdekat.
   - Menampilkan budget mingguan tersisa.
   - Memberi rekomendasi fokus harian.

2. **Schedule Manager**
   - Tambah/edit/hapus jadwal kuliah.
   - List jadwal per hari.
   - Simpan lokasi kelas: gedung, ruang, catatan rute.

3. **Task & Deadline Manager**
   - Tambah tugas dengan due date.
   - Status: pending, in_progress, done.
   - Priority scoring sederhana berdasarkan deadline dan estimasi durasi.
   - Breakdown tugas besar menjadi micro-task manual atau heuristic.

4. **Budget Tracker**
   - Set budget mingguan.
   - Catat pemasukan/pengeluaran.
   - Kategori: makan, transport, print/fotokopi, organisasi, hiburan, lain-lain.
   - Warning jika spending pace melebihi sisa minggu.

5. **Code Assignment Assessor**
   - Menjalankan file Python terhadap test cases.
   - Timeout protection.
   - Pass/fail report.
   - Basic lint/complexity summary dari project Personal Code Assessor.

### 6.2 Post-MVP Scope

1. Notes-to-Quiz.
2. PDF/material summarizer.
3. OCR import dari foto catatan.
4. Export jadwal ke `.ics`.
5. Web dashboard.
6. Claude custom commands di `.claude/commands`.
7. Weekly review generator.
8. Plugin/skill MabaOps untuk Claude Code.

---

## 7. User Stories

### 7.1 Daily Command Center

**As a** mahasiswa baru,  
**I want** melihat ringkasan hari ini dengan satu command,  
**so that** saya tahu kelas, deadline, dan budget tanpa buka banyak tempat.

Acceptance criteria:

- `mabaops today` menampilkan minimal: jadwal hari ini, top 3 deadline, budget remaining.
- Jika tidak ada data, app menampilkan onboarding prompt yang jelas.
- Output tetap readable di terminal Windows.

### 7.2 Schedule Management

**As a** mahasiswa,  
**I want** menyimpan jadwal kuliah lengkap dengan lokasi,  
**so that** saya tidak telat masuk kelas.

Acceptance criteria:

- User bisa tambah jadwal lewat CLI.
- User bisa list jadwal per hari.
- Data tetap ada setelah app ditutup.

### 7.3 Deadline Planning

**As a** mahasiswa yang sering mepet deadline,  
**I want** tahu tugas mana yang harus dikerjakan dulu,  
**so that** saya tidak salah prioritas.

Acceptance criteria:

- App menghitung priority score berdasarkan due date, status, dan estimasi waktu.
- Tugas yang due dalam 48 jam diberi label urgent.
- Tugas overdue ditampilkan jelas.

### 7.4 Budget Awareness

**As a** mahasiswa dengan uang mingguan terbatas,  
**I want** tahu pengeluaran saya masih aman atau tidak,  
**so that** saya bisa menyesuaikan spending sebelum telat.

Acceptance criteria:

- User bisa set weekly budget.
- User bisa tambah expense/income.
- `mabaops budget summary` menunjukkan total spent, remaining, dan warning.

### 7.5 Code Assignment Check

**As a** mahasiswa Informatika,  
**I want** mengecek tugas Python sebelum submit,  
**so that** saya bisa memperbaiki error lebih awal.

Acceptance criteria:

- `mabaops assess solution.py --cases test_cases/task1` menjalankan semua `.in/.out` pairs.
- App menampilkan jumlah passed/failed/timeouts.
- App membuat report markdown di `reports/`.

---

## 8. Core Commands

### 8.1 Global

```bash
mabaops --help
mabaops init
mabaops today
mabaops dashboard
```

### 8.2 Schedule

```bash
mabaops schedule add
mabaops schedule list
mabaops schedule today
mabaops schedule edit <id>
mabaops schedule delete <id>
```

### 8.3 Tasks

```bash
mabaops task add "Tugas Algoritma Array" --due 2026-09-25 --estimate 120
mabaops task list
mabaops task done <id>
mabaops task plan <id>
```

### 8.4 Budget

```bash
mabaops budget set-weekly 500000
mabaops budget add expense 15000 --category makan --note "nasi ayam"
mabaops budget add income 100000 --note "uang tambahan"
mabaops budget summary
```

### 8.5 Study

```bash
mabaops notes add notes/basis-data.md
mabaops quiz notes/basis-data.md
mabaops review-week
```

### 8.6 Code Assessor

```bash
mabaops assess tugas.py --cases test_cases/array
mabaops assess tugas.py --cases test_cases/array --timeout 2
```

---

## 9. UX Requirements

### 9.1 Interface Principles

1. **Terminal-first, beginner-friendly.**
2. **Default output harus ringkas.** Detail hanya muncul lewat flag seperti `--verbose`.
3. **Bahasa natural Indonesia boleh dipakai**, tapi command tetap konsisten bahasa Inggris untuk GitHub readability.
4. **No shame UX.** Hindari pesan seperti “kamu gagal”; gunakan “perlu perhatian”.
5. **Low friction.** Data entry harus bisa cepat, bukan form panjang.

### 9.2 TUI Dashboard Concept

```txt
╭──────────────────────────── MabaOps ────────────────────────────╮
│ Hari ini: Senin, Minggu ke-4 Semester 1                         │
├───────────────────────┬───────────────────────┬─────────────────┤
│ Jadwal Hari Ini        │ Deadline              │ Budget           │
│ 08:00 Algoritma A201   │ 2 hari: Tugas Array   │ Rp 72.000 left   │
│ 13:00 Kalkulus B104    │ 5 hari: Laporan PKKMB │ █████░░░ 58%     │
├───────────────────────┴───────────────────────┴─────────────────┤
│ Fokus: Kerjakan Tugas Array 45 menit sebelum Kalkulus.           │
╰──────────────────────────────────────────────────────────────────╯
```

---

## 10. Functional Requirements

### 10.1 Storage

- MVP menggunakan SQLite atau JSON lokal.
- Data harus portable di folder user project.
- Default path: `~/.mabaops/` atau `./data/` untuk mode repo/demo.
- App harus menyediakan sample data untuk demo GitHub.

### 10.2 Data Import/Export

- Export report markdown.
- Export backup JSON.
- Import schedule dari JSON/CSV pada post-MVP.

### 10.3 Offline Behavior

- Semua fitur inti harus berjalan offline.
- AI-assisted features bersifat optional.
- Jika API key tidak ada, fallback ke heuristic parser.

### 10.4 Error Handling

- Missing config: tampilkan instruksi `mabaops init`.
- Invalid date: tampilkan format contoh.
- Broken data file: buat backup dan minta user repair.
- Test case missing: tampilkan path yang dicari dan contoh struktur.

---

## 11. Non-Functional Requirements

### 11.1 Performance

- `mabaops today` harus selesai < 500ms untuk data lokal kecil.
- `mabaops task list` harus selesai < 500ms untuk 1.000 tugas.
- Code assessor timeout default 2 detik per test case.

### 11.2 Reliability

- Data write harus atomic jika memakai JSON.
- SQLite migration harus versioned jika memakai DB.
- App tidak boleh corrupt data saat command gagal.

### 11.3 Security & Privacy

- Data mahasiswa disimpan lokal secara default.
- Jangan upload catatan/tugas ke AI API tanpa user action eksplisit.
- API keys disimpan di `.env`, bukan hardcoded.
- `.env`, database lokal, dan reports personal harus masuk `.gitignore` jika sensitif.

### 11.4 Accessibility

- Output terminal harus readable tanpa warna.
- Warna hanya enhancement, bukan satu-satunya sinyal.
- Gunakan simbol + label teks untuk urgent/warning.

---

## 12. Data Model Draft

### 12.1 CourseSchedule

```json
{
  "id": "uuid",
  "course_code": "IF101",
  "course_name": "Algoritma dan Pemrograman",
  "lecturer": "Optional",
  "day": "Senin",
  "start_time": "08:00",
  "end_time": "10:30",
  "building": "Gedung A",
  "room": "A201",
  "notes": "Naik tangga kiri"
}
```

### 12.2 Task

```json
{
  "id": "uuid",
  "title": "Tugas Array",
  "description": "Implementasi operasi array dasar",
  "category": "coding",
  "course_code": "IF101",
  "due_date": "2026-09-25T23:59:00",
  "estimated_minutes": 120,
  "status": "pending",
  "priority_score": 87,
  "subtasks": []
}
```

### 12.3 BudgetEntry

```json
{
  "id": "uuid",
  "type": "expense",
  "amount": 15000,
  "category": "makan",
  "note": "Nasi ayam kantin",
  "created_at": "2026-09-19T12:30:00"
}
```

### 12.4 StudyNote

```json
{
  "id": "uuid",
  "title": "Basis Data - Normalisasi",
  "path": "notes/basis-data.md",
  "course_code": "IF102",
  "tags": ["database", "normalisasi"],
  "created_at": "2026-09-19T20:00:00"
}
```

### 12.5 AssessmentReport

```json
{
  "id": "uuid",
  "target_file": "my_tasks/solution.py",
  "cases_dir": "test_cases/task1",
  "passed": 8,
  "failed": 2,
  "timeouts": 0,
  "score": 82,
  "report_path": "reports/task1-assessment.md",
  "created_at": "2026-09-19T21:00:00"
}
```

---

## 13. Technical Recommendation

### 13.1 MVP Stack

Recommended:

- **Language:** Python 3.11+
- **CLI:** Typer
- **Terminal UI:** Rich first, Textual later
- **Storage:** SQLite via SQLModel or plain SQLite; JSON acceptable for first prototype
- **Validation:** Pydantic
- **Testing:** pytest
- **Packaging:** pyproject.toml

Rationale:

- User already has strong Python CLI experience.
- Existing Personal Code Assessor can be reused.
- TUI screenshots look strong in GitHub README.
- Easier to finish than full-stack web.

### 13.2 Suggested Repository Structure

```txt
mabaops/
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   └── mabaops/
│       ├── __init__.py
│       ├── cli.py
│       ├── tui.py
│       ├── config.py
│       ├── storage.py
│       ├── models.py
│       ├── schedule/
│       │   ├── manager.py
│       │   └── views.py
│       ├── tasks/
│       │   ├── manager.py
│       │   ├── priority.py
│       │   └── planner.py
│       ├── budget/
│       │   ├── manager.py
│       │   └── reports.py
│       ├── study/
│       │   ├── notes.py
│       │   ├── quiz.py
│       │   └── review.py
│       └── assessor/
│           ├── executor.py
│           ├── linter.py
│           ├── complexity.py
│           └── reporter.py
├── data/
│   ├── schedule.example.json
│   ├── tasks.example.json
│   └── budget.example.json
├── reports/
├── tests/
├── docs/
│   ├── PRD-MabaOps.md
│   ├── ROADMAP.md
│   └── ARCHITECTURE.md
└── screenshots/
```

---

## 14. Claude Code-Native Layer

MabaOps should include a `.claude/` folder for repo-specific AI workflows.

### 14.1 Suggested Custom Commands

```txt
.claude/commands/
├── mabaops-plan-week.md
├── mabaops-review-week.md
├── mabaops-assess-feature.md
└── mabaops-github-polish.md
```

Example command intent:

- `/mabaops-plan-week`: read sample data and generate realistic weekly plan.
- `/mabaops-review-week`: summarize completed tasks, missed tasks, budget risk.
- `/mabaops-assess-feature`: review new feature against PRD acceptance criteria.
- `/mabaops-github-polish`: improve README, screenshots, and demo script.

### 14.2 Suggested Agents

```txt
.claude/agents/
├── student-product-manager.md
├── code-assessor.md
└── study-coach.md
```

---

## 15. MVP Milestones

### Milestone 1: Project Foundation

Deliverables:

- Python package skeleton.
- `mabaops --help` works.
- Config/data directory initialized.
- README with screenshot placeholder.

Exit criteria:

- `pytest` passes.
- `mabaops init` creates required local files.

### Milestone 2: Schedule + Today

Deliverables:

- Add/list schedule.
- `mabaops today` shows schedule for current day.

Exit criteria:

- Sample schedule produces stable today output.

### Milestone 3: Tasks + Priority

Deliverables:

- Add/list/complete tasks.
- Priority score.
- Urgent/overdue labels.

Exit criteria:

- Tasks due soon rank above low-risk tasks.

### Milestone 4: Budget

Deliverables:

- Weekly budget config.
- Expense/income entries.
- Budget summary.

Exit criteria:

- Budget warning triggers when spending pace is unsafe.

### Milestone 5: TUI Dashboard

Deliverables:

- Rich dashboard for `mabaops dashboard`.
- Screenshot-ready terminal output.

Exit criteria:

- Dashboard fits standard terminal width.
- Works on Windows terminal.

### Milestone 6: Code Assessor

Deliverables:

- Basic Python test runner.
- Markdown report.
- Timeout protection.

Exit criteria:

- Sample passing/failing solutions generate expected report.

### Milestone 7: GitHub Polish

Deliverables:

- README final.
- Demo data.
- Screenshot.
- Roadmap.
- License.

Exit criteria:

- Fresh clone can run demo commands using documented steps.

---

## 16. Success Metrics

### 16.1 Product Metrics

- User can answer “what should I do now?” in under 10 seconds.
- User can add a task in under 30 seconds.
- Weekly review gives at least 3 actionable insights.
- Code assessor catches at least one failure before submission in demo scenario.

### 16.2 GitHub/Portfolio Metrics

- README explains value proposition in first 10 lines.
- Repo has screenshot/GIF demo.
- Setup takes < 5 minutes on a fresh machine.
- Project structure looks professional to recruiters/peers.

---

## 17. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Scope terlalu besar | High | MVP dibatasi ke CLI + 5 modul inti |
| AI dependency bikin susah demo | Medium | Semua core features harus offline |
| Data model berubah terus | Medium | Mulai dari SQLite/JSON sederhana + migration later |
| TUI terlalu lama | Medium | Pakai Rich dashboard dulu, Textual setelah MVP |
| Repo existing bercampur dengan project lain | High | Buat docs dan branch PRD dulu, lalu putuskan rename/pivot |
| Budget/category terlalu rumit | Low | Pakai kategori default sederhana |

---

## 18. Open Questions

1. Apakah MabaOps akan menjadi repo baru atau pivot dari repo existing?
2. Apakah MVP harus Python CLI/TUI atau full-stack web?
3. Apakah data default disimpan di `./data` untuk demo atau `~/.mabaops` untuk real use?
4. Apakah AI features wajib di MVP atau post-MVP?
5. Apakah target bahasa UI utama Indonesia, English, atau hybrid?

Jawaban sementara:

1. Repo baru atau clean branch lebih ideal.
2. Python CLI/TUI untuk MVP.
3. Dukung dua mode: `./data` untuk demo, `~/.mabaops` untuk user.
4. AI post-MVP, kecuali simple heuristic.
5. Hybrid: command English, copy UX Indonesia.

---

## 19. Launch Plan

### 19.1 Internal Demo

Demo script:

1. `mabaops init --demo`
2. `mabaops today`
3. `mabaops task add "Tugas Array" --due 2026-09-25 --estimate 120`
4. `mabaops budget add expense 15000 --category makan`
5. `mabaops dashboard`
6. `mabaops assess examples/solution.py --cases examples/test_cases/array`

### 19.2 GitHub Release Checklist

- [ ] README with value proposition.
- [ ] Installation guide.
- [ ] Demo commands.
- [ ] Screenshot/GIF.
- [ ] Example data.
- [ ] Roadmap.
- [ ] License.
- [ ] Contributing guide optional.

---

## 20. Final Recommendation

Build **MabaOps MVP as a Python local-first CLI/TUI**, not full-stack web first. The product should focus on daily clarity for mahasiswa baru: today dashboard, schedule, deadline priority, budget awareness, and code assignment assessment.

This is the strongest fit because it combines the user’s existing projects, matches the Claude Code-heavy development environment, and creates a GitHub repo with a clear story:

> “I built a student-life operating system for Indonesian freshmen, with local-first productivity tools and code-assignment assessment.”
