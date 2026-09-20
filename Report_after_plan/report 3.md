# Report 3 & Session Handover — MabaOps Plan 3 (Task Manager & Priority Engine)

Tanggal: 2026-09-19  
Lokasi project: `C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk`

---

## 1. Status Terkini Proyek MabaOps

- **Plan 1 (Foundation):** Selesai 100% (Skeleton, CLI Typer, `init`, `init --demo`, `today` dashboard basic, pytest 4 passed).
- **Plan 2 (Schedule Manager):** Selesai 100% (`mabaops schedule add`, `list`, `today`, normalisasi hari, pytest 8 passed).
- **Plan 3 (Task Manager & Priority Engine):** Selesai 100% (17-09-2026 update).
  - **Storage & Priority Engine:** Selesai (`TaskItem` model dengan `priority_score` dan `urgency_label`, `load_tasks`, `save_tasks`, `add_task_item`, `update_task_status`, `parse_due_date`, kalkulasi skor prioritas berdasarkan overdue, urgent < 48 jam, dan estimasi waktu).
  - **CLI Commands (`mabaops task`):** Selesai (`task add`, `task list [--status] [--course]`, `task start`, `task done` dengan ID prefix matching; `today` menampilkan top 3 task terurut `priority_score`).
  - **Tests:** Selesai — 14 tests passed, termasuk coverage priority sorting, label OVERDUE/URGENT, filter status, ID tidak ditemukan (exit 1), dan rendering task di `today`.
  - **Dokumentasi:** README.md diperbarui dengan tabel Priority Engine dan format `--due` yang didukung.

---

## 2. Handover Guide untuk Sesi Berikutnya

Jika Anda melanjutkan sesi ini atau memulai sesi baru, ikuti petunjuk operasional berikut:

### 2.1 File Penting yang Sudah Dibuat
- `src/mabaops/models.py`: Berisi model Pydantic (`CourseSchedule`, `TaskItem`, `BudgetConfig`, dll.).
- `src/mabaops/storage.py`: Berisi manajemen JSON storage, kalkulasi prioritas task, dan manajemen jadwal.
- `src/mabaops/cli.py`: Berisi Typer CLI app (perlu ditambahkan subcommand `task` untuk melengkapi Plan 3).
- `tests/test_cli.py`: Berisi unit/integration tests.
- `report 1.md` & `report 2.md`: Laporan progres Plan 1 dan Plan 2.

### 2.2 Langkah Sisa untuk Menyelesaikan Plan 3

**✅ SELESAI (17-09-2026):** Semua item di bawah ini sudah dieksekusi dan terverifikasi:

1. ~~CLI Command `task` di `src/mabaops/cli.py`~~ — `task add/list/done/start` + integrasi `today` top 3 by `priority_score`.
2. ~~Test Case di `tests/test_cli.py`~~ — 5 test baru ditambahkan (priority sorting, overdue/urgent labels, filter status, unknown ID, today rendering).
3. ~~Jalankan Pytest~~ — **14 passed in ~2s**.
4. ~~Update `README.md`~~ — Tabel Priority Engine + format `--due` didokumentasikan.

### 2.3 Quick Verification Command
```powershell
cd "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk"
.\.venv\Scripts\python.exe -m pytest tests
```

Hasil terakhir: **14 passed** — Plan 3 resmi selesai.

---

## 3. Update: Plan 4 (Budget Tracker) — Selesai

Tanggal: 2026-09-20

### 3.1 Yang Diimplementasikan
- **Storage (`src/mabaops/storage.py`):**
  - `load_budget`, `save_budget`, `set_weekly_budget` (validasi non-negatif).
  - `load_budget_entries`, `save_budget_entries`, `add_budget_entry` (tipe expense/income, amount > 0, kategori dinormalisasi).
  - `normalize_category` + `EXPENSE_CATEGORIES`: makan, transport, print, organisasi, hiburan, lain-lain (dengan alias: minum→makan, fotokopi→print, dll.).
  - `budget_summary`: hitung entri minggu berjalan (sejak Senin), spent/income/remaining, pace harian, proyeksi akhir minggu, dan status (`safe` / `warning` / `deficit` / `no_budget`).
- **CLI (`src/mabaops/cli.py`):**
  - `mabaops budget set-weekly <amount>`
  - `mabaops budget add <expense|income> <amount> [-c kategori] [-n catatan]`
  - `mabaops budget summary` dengan tabel Rich + pesan status no-shame UX.
- **Tests:** 4 test baru (set-weekly & add entries, validasi tipe/kategori, safe & deficit summary, hint setup saat budget kosong).
- **Dokumentasi:** README.md diperbarui dengan seksi Budget + status 18 tests passed.

### 3.2 Hasil Verifikasi
- **Pytest: 18 passed** (dari 14).
- Warning logic bersifat deterministik di test (skenario deficit), pace warning tergantung hari eksekusi.

### 3.3 Update: Plan 5 (TUI Dashboard) — Selesai

Tanggal: 2026-09-20

**Yang Diimplementasikan:**
- **CLI (`src/mabaops/cli.py`):** command `mabaops dashboard` dengan Rich layout:
  - Header panel tanggal/hari.
  - 3-panel Columns: Jadwal Hari Ini (cyan) | Deadline Prioritas (yellow, label URGENT/OVERDUE berwarna) | Budget (magenta, dengan progress bar ASCII `#---` dan persentase usage).
  - Saran fokus harian di bawah (reuse `focus_message`).
  - Fallback panel setup jika data belum di-init.
- **Fix Windows legacy console:** progress bar pakai karakter ASCII (`#`/`-`) bukan `█`/`░` untuk menghindari `UnicodeEncodeError` cp1252 — sesuai NFR accessibility PRD (output readable tanpa simbol khusus).
- **Tests:** 3 test baru (dashboard demo data render 3 panel, dashboard tanpa data prompt init, budget bar & amount). Total **21 passed**.
- **Dokumentasi:** README.md diperbarui (seksi dashboard, command list, status 21 tests passed).

**Next: Plan 6 (Code Assessor)** sesuai PRD Milestone 6:
- `mabaops assess <file.py> --cases <dir>` menjalankan pasangan `.in/.out`.
- Timeout protection (default 2 detik per case), pass/fail/timeout report.
- Markdown report di `reports/`.

### 3.4 Update: Plan 6 (Code Assessor) — Selesai

Tanggal: 2026-09-20

**Yang Diimplementasikan:**
- **Modul baru `src/mabaops/assessor.py`:**
  - `discover_cases`: scan pasangan `*.in` + `*.out` di directory (validasi struktur + pesan error jelas).
  - `run_case`: eksekusi solusi via subprocess dengan stdin dari `.in`, bandingkan stdout dengan `.out` (strip whitespace), timeout per case (default 2 detik), deteksi error via return code.
  - `assess_solution`: agregasi passed/failed/timeouts/errors + skor persentase.
  - `write_report`: markdown report dengan tabel per case (status, durasi, detail) di `reports/`.
- **CLI:** `mabaops assess <file.py> --cases <dir> [--timeout] [--report-dir]` — tabel Rich hasil per case, skor summary, exit code 1 jika ada kegagalan.
- **Tests:** 3 test baru via fixture `assess_env` (mixed pass/fail/timeout + report content, all-pass exit 0, cases dir tidak ada). Total **24 passed**.
- **Fix kecil:** import `Path` di `cli.py`; validasi `--cases` diserahkan ke handler (bukan `exists=True` Typer) agar pesan error konsisten.
- **Dokumentasi:** README.md diperbarui (seksi Code Assessor + struktur test case).

**Status: MVP Milestone 1-6 PRD selesai semua.** Sisa: Milestone 7 (GitHub polish — README final, screenshot, demo data, roadmap, license).