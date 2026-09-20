# Report 1 — Status Plan 1 MabaOps

Tanggal: 2026-09-19 , 21:35
Lokasi project: `C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk`

---

## 1. Ringkasan Status Saat Ini

Plan 1 untuk project **MabaOps** sudah dikerjakan sampai tahap foundation berjalan.

Target Plan 1 adalah membuat pondasi awal aplikasi Python CLI local-first sesuai PRD:

- Python package skeleton.
- CLI command `mabaops --help`.
- CLI command `mabaops init`.
- CLI command `mabaops init --demo`.
- CLI command `mabaops today`.
- Storage awal berbasis JSON lokal.
- Test dasar untuk perilaku CLI foundation.

Status saat ini: **Plan 1 selesai dan sudah divalidasi dengan pytest + smoke test CLI.**

---

## 2. Keputusan Implementasi Plan 1

Berdasarkan Plan 0 yang sudah di-ACC, implementasi Plan 1 mengikuti arah berikut:

- Bahasa utama: **Python**.
- Minimum Python: **Python 3.11+**.
- CLI framework: **Typer**.
- Terminal rendering: **Rich**.
- Data validation/model: **Pydantic**.
- Test framework: **pytest**.
- Storage MVP awal: **JSON lokal**.
- Mode data default: `./data` untuk repo/demo.
- AI features: belum dimasukkan ke MVP foundation.

Catatan penting:

- Implementasi dikerjakan langsung di direktori utama `Projek_Ngantuk`, sesuai instruksi user.
- Tidak menggunakan isolated worktree untuk hasil final Plan 1.
- Belum ada commit git yang dibuat.

---

## 3. File dan Folder yang Sudah Dibuat

Berikut struktur penting yang sudah dibuat atau ditambahkan:

```txt
Projek_Ngantuk/
├── PRD-MabaOps.md
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── report 1.md
├── .venv/
├── data/
│   ├── schedule.json
│   ├── tasks.json
│   ├── budget.json
│   └── budget_entries.json
├── docs/
├── src/
│   └── mabaops/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       └── storage.py
└── tests/
    └── test_cli.py
```

---

## 4. Detail File yang Dibuat

### 4.1 `pyproject.toml`

Fungsi:

- Mendefinisikan package Python bernama `mabaops`.
- Mengatur build backend menggunakan `hatchling`.
- Mendefinisikan dependency utama:
  - `typer`
  - `rich`
  - `pydantic`
- Mendefinisikan dependency development:
  - `pytest`
- Menambahkan console script:

```toml
[project.scripts]
mabaops = "mabaops.cli:app"
```

Artinya setelah package di-install, command berikut tersedia:

```bash
mabaops
```

---

### 4.2 `.gitignore`

Fungsi:

- Mengabaikan cache Python.
- Mengabaikan virtual environment.
- Mengabaikan build output.
- Mengabaikan `.env`.
- Mengabaikan beberapa local/sensitive output seperti `.mabaops/` dan generated reports.

---

### 4.3 `.env.example`

Fungsi:

- Placeholder untuk konfigurasi masa depan.
- Saat ini berisi contoh:

```env
# ANTHROPIC_API_KEY=
# MABAOPS_DATA_DIR=./data
```

AI belum dipakai di Plan 1, tapi file ini disiapkan untuk post-MVP/future optional AI feature.

---

### 4.4 `README.md`

Fungsi:

- Menjelaskan value proposition awal MabaOps.
- Menyediakan Quick Start awal:

```bash
pip install -e .[dev]
mabaops --help
mabaops init --demo
mabaops today
```

- Menjelaskan mode data default `./data` dan override `--data-dir`.

---

### 4.5 `src/mabaops/__init__.py`

Fungsi:

- Menandai `mabaops` sebagai package Python.
- Menyimpan version awal:

```python
__version__ = "0.1.0"
```

---

### 4.6 `src/mabaops/__main__.py`

Fungsi:

- Membuat package bisa dijalankan via:

```bash
python -m mabaops
```

---

### 4.7 `src/mabaops/config.py`

Fungsi:

- Menangani resolusi direktori data lokal.
- Prioritas data directory:
  1. Argumen CLI `--data-dir`.
  2. Environment variable `MABAOPS_DATA_DIR`.
  3. Default `./data`.

---

### 4.8 `src/mabaops/models.py`

Fungsi:

- Mendefinisikan model data awal menggunakan Pydantic.

Model yang sudah dibuat:

- `CourseSchedule`
- `TaskItem`
- `BudgetConfig`
- `BudgetEntry`
- `AppData`

Model ini menjadi pondasi untuk modul berikutnya:

- Schedule Manager.
- Task Manager.
- Budget Tracker.
- Today Dashboard.

---

### 4.9 `src/mabaops/storage.py`

Fungsi:

- Menangani storage JSON lokal.
- Menyediakan atomic-ish write via temporary file lalu replace.
- Menyediakan payload kosong dan payload demo.
- Menyediakan loader untuk gabungan data aplikasi.

File JSON yang dikelola:

- `schedule.json`
- `tasks.json`
- `budget.json`
- `budget_entries.json`

Fungsi penting:

- `ensure_data_dir`
- `read_json`
- `write_json`
- `init_storage`
- `empty_payloads`
- `demo_payloads`
- `load_app_data`
- `indonesian_day_name`

---

### 4.10 `src/mabaops/cli.py`

Fungsi:

- Menyediakan CLI utama berbasis Typer.
- Menggunakan Rich untuk output terminal.

Command yang sudah tersedia:

```bash
mabaops --help
mabaops init
mabaops init --demo
mabaops today
```

#### `mabaops init`

Membuat data file kosong di data directory.

#### `mabaops init --demo`

Membuat data demo untuk kebutuhan trial/screenshot.

Data demo berisi:

- Jadwal Algoritma dan Pemrograman.
- Jadwal Kalkulus Dasar.
- Tugas Array.
- Resume Materi PKKMB.
- Budget mingguan Rp 500.000.
- Pengeluaran demo Rp 15.000.

#### `mabaops today`

Menampilkan ringkasan hari ini berupa table Rich:

- Jadwal hari ini.
- Deadline/top tasks.
- Budget weekly/spent/left.
- Fokus harian sederhana.

---

### 4.11 `tests/test_cli.py`

Fungsi:

- Menyediakan test foundation untuk CLI awal.

Test yang dibuat:

1. `test_help_shows_mabaops`
2. `test_init_demo_creates_data_files`
3. `test_today_without_data_prompts_init`
4. `test_today_with_demo_data_outputs_dashboard`

---

## 5. Virtual Environment

Virtual environment lokal sudah dibuat di:

```txt
C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk\.venv
```

Package sudah di-install editable dengan dependency development.

Command install yang dijalankan:

```powershell
& "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk\.venv\Scripts\python.exe" -m pip install -e "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk[dev]"
```

Hasil:

- Package `mabaops==0.1.0` berhasil dibuild dan di-install editable.
- Dependency berhasil terinstall:
  - `typer`
  - `rich`
  - `pydantic`
  - `pytest`
  - dependency transitif lain.

Catatan issue yang sempat ditemukan:

- `pyproject.toml` awalnya ditulis dengan UTF-8 BOM dari PowerShell 5.1.
- `tomllib` menolak BOM dan menghasilkan error:

```txt
TOMLDecodeError: Invalid statement (at line 1, column 1)
```

Fix yang dilakukan:

- Semua file teks penting direwrite sebagai **UTF-8 tanpa BOM**.
- Setelah itu install editable berhasil.

---

## 6. Test yang Sudah Dijalankan

### 6.1 Pytest Suite

Command yang dijalankan:

```powershell
$root = "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk"
& "$root\.venv\Scripts\python.exe" -m pytest "$root\tests"
```

Hasil test:

```txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk
configfile: pyproject.toml
collected 4 items

Projek_Ngantuk\tests\test_cli.py ....                                    [100%]

============================== 4 passed in 1.06s ==============================
```

Status: **PASS**

Test coverage saat ini fokus pada foundation behavior, bukan coverage persentase formal.

---

### 6.2 Smoke Test CLI

Command yang dijalankan:

```powershell
$root = "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk"
& "$root\.venv\Scripts\mabaops.exe" --help
& "$root\.venv\Scripts\mabaops.exe" init --demo --data-dir "$root\data"
& "$root\.venv\Scripts\mabaops.exe" today --data-dir "$root\data"
```

Hasil smoke test:

- `mabaops --help` berhasil menampilkan command:
  - `init`
  - `today`
- `mabaops init --demo` berhasil membuat/memperbarui file data:
  - `schedule.json`
  - `tasks.json`
  - `budget.json`
  - `budget_entries.json`
- `mabaops today` berhasil menampilkan dashboard ringkas.

Contoh output penting dari `today`:

```txt
MabaOps Today - Sabtu

Jadwal Hari Ini:
- 08:00 Algoritma dan Pemrograman (A201)
- 13:00 Kalkulus Dasar (B104)

Deadline:
- 2026-09-25 - Tugas Array
- 2026-09-28 - Resume Materi PKKMB

Budget:
- Weekly: Rp 500.000
- Spent: Rp 15.000
- Left: Rp 485.000

Fokus: Kerjakan satu tugas prioritas selama 25-45 menit.
```

Status: **PASS**

---

## 7. Git Status Saat Ini

Command yang dijalankan:

```powershell
git status --short -- "Projek_Ngantuk"
```

Hasil:

```txt
?? Projek_Ngantuk/
```

Artinya:

- Folder `Projek_Ngantuk/` masih untracked dari perspektif git repository utama.
- Belum ada commit yang dibuat.
- Ini sesuai karena user meminta kerja langsung di direktori utama, dan belum meminta commit.

---

## 8. Command yang Bisa Dicoba User

Dari direktori project:

```powershell
cd "C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk"
```

Jalankan help:

```powershell
.\.venv\Scripts\mabaops.exe --help
```

Initialize demo data:

```powershell
.\.venv\Scripts\mabaops.exe init --demo --data-dir .\data
```

Lihat dashboard hari ini:

```powershell
.\.venv\Scripts\mabaops.exe today --data-dir .\data
```

Jalankan test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

---

## 9. Batasan Plan 1 Saat Ini

Yang sudah ada:

- CLI foundation.
- Data directory setup.
- Demo data generation.
- JSON storage awal.
- Today dashboard basic.
- Foundation tests.

Yang belum ada dan masuk Plan berikutnya:

- `mabaops schedule add`
- `mabaops schedule list`
- `mabaops schedule today`
- `mabaops task add`
- `mabaops task list`
- `mabaops task done`
- Priority scoring task.
- Budget command lengkap.
- Rich dashboard final via `mabaops dashboard`.
- Code assignment assessor.

---

## 10. Rekomendasi Next Step

Next step paling natural adalah lanjut ke **Plan 2 — Schedule + Today Dashboard Basic**.

Target Plan 2:

```bash
mabaops schedule add
mabaops schedule list
mabaops schedule today
mabaops today
```

Prioritas implementasi Plan 2:

1. Tambah Typer subcommand group `schedule`.
2. Buat fungsi tambah jadwal ke `schedule.json`.
3. Buat list jadwal semua/per hari.
4. Buat `schedule today`.
5. Integrasikan output yang lebih rapi ke `today`.
6. Tambah test untuk schedule commands.

---

## 11. Status Akhir

Plan 1 sudah selesai dengan hasil validasi:

- Pytest: **4 passed**.
- CLI help: **PASS**.
- Init demo data: **PASS**.
- Today dashboard: **PASS**.
- Package editable install: **PASS** setelah fix UTF-8 BOM.

Kesimpulan:

**MabaOps sekarang sudah punya pondasi Python CLI yang bisa dijalankan, diuji, dan dikembangkan ke modul Schedule pada Plan 2.**
