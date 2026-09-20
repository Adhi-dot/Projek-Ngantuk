# MabaOps

**Student life operating system for Indonesian college freshmen.**

MabaOps is a local-first CLI/TUI command center for jadwal kuliah, deadline tugas, budget mingguan, catatan belajar, and coding assignment checks.

> One command to answer: *“Hari ini aku harus ngapain?”*

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## Screenshot

<!-- TODO: Tambahkan screenshot `mabaops dashboard` di screenshots/ -->

```text
+------------------+
| Hari ini: Senin  |
+------------------+
+--- Jadwal Hari Ini ---+ +--- Deadline Prioritas ---+ +--- Budget ---+
| 08:00-10:30 IF101     | | URGENT 2026-09-21        | | Left: 485k   |
| Algoritma (A201)      | | Tugas Array              | | -----  3%    |
+-----------------------+ +--------------------------+ +--------------+

Fokus: Kerjakan satu tugas prioritas selama 25-45 menit.
```

## Quick Demo (Fresh Clone)

**Windows (one-click):**

```bat
git clone <repo-url> && cd mabaops
setup.bat

mabaops.bat dashboard
```

Atau manual (semua OS):

```bash
git clone <repo-url> && cd mabaops
pip install -e .[dev]

mabaops init --demo   # data contoh
mabaops today         # ringkasan harian
mabaops dashboard     # TUI 3-panel

# Cek tugas coding (sample test cases & solution sudah disertakan!)
mabaops assess solution.py --cases test_cases/array

pytest                # 28 passed
```

## Features (Current Progress)

- **Plan 1 (Foundation):** CLI framework, config resolution, local JSON storage, `init`, `init --demo`, and `today` snapshot.
- **Plan 2 (Schedule Manager):** Add course schedule, filter/list by day, today's schedule view with classroom/building locations.
- **Plan 3 (Task Manager & Priority Engine):** Task addition with deadline parsing, auto-priority scoring (`OVERDUE`, `URGENT` < 48h, `OK`), status updates (`start`, `done`), and top priority task integration in `today`.
- **Plan 4 (Budget Tracker):** Weekly budget config, expense/income entries dengan kategori, dan budget summary dengan spending pace warning.
- **Plan 5 (TUI Dashboard):** `mabaops dashboard` dengan Rich 3-panel layout (Jadwal | Deadline Prioritas | Budget) + progress bar & fokus harian.
- **Plan 6 (Code Assessor):** `mabaops assess` menjalankan solusi Python terhadap pasangan `.in/.out` dengan timeout protection, tabel hasil, skor, dan markdown report di `reports/`.
- **Web Dashboard (local):** `mabaops web` — full CRUD dari browser di localhost: tambah/hapus jadwal, tugas (start/done), dan entri budget. Data tetap local-first di JSON yang sama dengan CLI.

## Quick Start

```bash
pip install -e .[dev]

# Inisialisasi awal (atau pakai --demo untuk data contoh)
mabaops init --demo

# Lihat ringkasan hari ini (jadwal & top tasks)
mabaops today

# TUI dashboard (3-panel: jadwal, deadline, budget)
mabaops dashboard

# Cek tugas coding sebelum submit
mabaops assess solution.py --cases test_cases/array --timeout 2

# Kelola jadwal kuliah
mabaops schedule list
mabaops schedule today
mabaops schedule add -c IF102 -n "Struktur Data" -d Senin --start 09:00 --end 10:40 -b "Gedung C" -r "C301" --notes "Bawa laptop"

# Kelola tugas & deadline
mabaops task list
mabaops task add "Tugas Basis Data" --due 2026-09-30 --estimate 90 --course IF103
mabaops task start <task_id>
mabaops task done <task_id>

# Kelola budget mingguan
mabaops budget set-weekly 500000
mabaops budget add expense 15000 -c makan -n "nasi ayam kantin"
mabaops budget add income 50000 -n "uang tambahan"
mabaops budget summary
```

## Available Commands

### General
- `mabaops --help` : Bantuan umum
- `mabaops init [--demo]` : Setup direktori data lokal
- `mabaops today` : Dashboard ringkas harian (jadwal, deadline prioritas, budget, saran fokus)
- `mabaops dashboard` : TUI dashboard Rich 3-panel dengan warna, progress bar budget, dan saran fokus
- `mabaops web [--port 8000]` : Web dashboard CRUD di localhost (butuh `pip install -e .[web]`)

### Schedule (`mabaops schedule`)
- `mabaops schedule add` : Tambah jadwal kuliah baru (dukung `--lecturer` / `-l`)
- `mabaops schedule list [-d <Hari>]` : Tampilkan seluruh jadwal atau filter per hari
- `mabaops schedule today` : Tampilkan jadwal khusus hari ini
- `mabaops schedule delete <code|id>` : Hapus jadwal berdasarkan kode MK atau prefix ID

### Task (`mabaops task`)
- `mabaops task add <title> --due <date> [--estimate <mins>] [--course <code>] [--category <cat>]` : Tambah tugas baru dengan prioritas otomatis
- `mabaops task list [--status <status>] [--course <code>]` : List tugas diurutkan berdasarkan priority score tertinggi
- `mabaops task start <id_prefix>` : Tandai tugas sedang dikerjakan (`in_progress`)
- `mabaops task done <id_prefix>` : Tandai tugas selesai (`done`)
- `mabaops task plan <id_prefix>` : Breakdown tugas besar menjadi actionable micro-tasks otomatis (heuristic)

#### Priority Engine
Setiap tugas otomatis diberi `priority_score` dan `urgency_label` berdasarkan deadline & estimasi waktu:

| Label | Kondisi | Skor |
|---|---|---|
| `OVERDUE` | Lewat deadline | 1000+ (naik per jam keterlambatan) |
| `URGENT` | Deadline ≤ 48 jam | 500+ (bonus makin mepet & estimasi besar) |
| `OK` | Deadline > 48 jam | 100+ (bonus kedekatan & estimasi) |
| `DONE` | Status selesai | -1 (tidak muncul di `today`) |

Format `--due` yang didukung: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM`, atau `YYYY-MM-DDTHH:MM`.

### Budget (`mabaops budget`)
- `mabaops budget set-weekly <amount>` : Set budget mingguan
- `mabaops budget add <expense|income> <amount> [-c <kategori>] [-n <catatan>]` : Catat pengeluaran/pemasukan
- `mabaops budget summary` : Ringkasan minggu ini (spent, sisa, pace harian, proyeksi akhir minggu)

Kategori expense: `makan` (termasuk minum), `transport`, `print` (termasuk fotokopi), `organisasi`, `hiburan`, `lain-lain`.

Status summary:
- **Aman** : pace pengeluaran masih sesuai budget
- **Perlu perhatian (warning)** : proyeksi akhir minggu melebihi budget
- **Perlu perhatian (deficit)** : pengeluaran sudah melebihi budget + pemasukan

Hanya entri minggu berjalan (sejak Senin) yang dihitung dalam summary.

### Code Assessor (`mabaops assess`)
- `mabaops assess <file.py> --cases <dir> [--timeout <detik>]` : Jalankan solusi terhadap semua pasangan `.in/.out` di directory

Struktur test case yang diharapkan:

```text
test_cases/array/
├── case1.in    # input stdin
├── case1.out   # output yang diharapkan
├── case2.in
└── case2.out
```

Hasil per case: `passed` (output cocok), `failed` (output beda), `timeout` (lewat batas waktu, default 2 detik), atau `error` (crash). Exit code `1` jika ada case gagal. Markdown report otomatis disimpan di `reports/`.

## Data Mode

Secara default, data disimpan di `./data`. Untuk override lokasi:

```bash
mabaops init --data-dir ~/.mabaops
mabaops today --data-dir ~/.mabaops
```

## Running Tests

```bash
pytest
```

Status saat ini: **28 tests passed** (Plan 1-6 / MVP Milestone 1-6 + Comprehensive Security & PRD Alignment).

## Panduan Lengkap

Panduan penggunaan lengkap semua command ada di [docs/USAGE.md](docs/USAGE.md).

## Project Structure

```text
mabaops/
├── src/mabaops/
│   ├── cli.py          # Typer CLI (today, dashboard, schedule, task, budget, assess)
│   ├── storage.py      # JSON storage + priority engine + budget summary
│   ├── models.py       # Pydantic models
│   ├── config.py       # Data dir resolution
│   └── assessor.py     # Code assessor (.in/.out runner + report)
├── tests/
├── docs/ROADMAP.md
├── data/               # Data lokal (dibuat via mabaops init)
└── reports/            # Markdown assessment reports
```

## License

[MIT](LICENSE)