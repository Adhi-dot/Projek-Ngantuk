# Report 2 — Status Plan 2 MabaOps (Schedule Manager & Today Integration)

Tanggal: 2026-09-19  
Lokasi project: `C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk`

---

## 1. Ringkasan Eksekusi Plan 2

Plan 2 berfokus pada implementasi modul **Schedule Manager** dan integrasinya dengan dashboard harian `mabaops today`.

Fitur yang berhasil diselesaikan pada Plan 2:
1. **Subcommand Group `mabaops schedule`**:
   - `mabaops schedule add`: Tambah mata kuliah, hari, jam, gedung, ruangan, catatan.
   - `mabaops schedule list`: Menampilkan seluruh jadwal kuliah atau difilter per hari (`-d / --day`).
   - `mabaops schedule today`: Menampilkan jadwal khusus hari ini.
2. **Storage & Normalization Engine**:
   - Helper storage untuk read, write, sorting urutan hari (Senin–Minggu) dan jam.
   - Normalisasi nama hari bahasa Indonesia (misal: "jum'at" / "ahad" → "Jumat" / "Minggu").
   - Validasi nama hari agar mencegah data corrupt.
3. **Integrasi Today Dashboard**:
   - Formatting lokasi kelas (`Gedung + Ruang` atau fallback yang ada).
   - Format waktu dan nama mata kuliah yang rapi pada table Rich.
4. **Unit & Integration Tests**:
   - Penambahan test case untuk schedule add, list, filtering hari, schedule today, dan validation error.
5. **Dokumentasi**:
   - Update `README.md` dengan panduan penggunaan command `schedule`.

Status saat ini: **Plan 2 selesai 100% dan seluruh 8 test lulus.**

---

## 2. File yang Ditambahkan / Diperbarui

```txt
Projek_Ngantuk/
├── README.md                 (Diperbarui: docs command schedule & options)
├── report 2.md               (Baru: laporan detail Plan 2)
├── src/
│   └── mabaops/
│       ├── storage.py        (Diperbarui: load/save/add/filter/normalize schedule)
│       └── cli.py            (Diperbarui: schedule add/list/today commands)
└── tests/
    └── test_cli.py           (Diperbarui: +4 test cases untuk schedule)
```

---

## 3. Detail Implementasi & Command Baru

### 3.1 `mabaops schedule add`
Menambahkan jadwal kuliah baru ke `schedule.json`.

**Parameter & Flags:**
- `-c, --course-code` *(Wajib)*: Kode MK (contoh: `IF101`, `IF102`)
- `-n, --course-name` *(Wajib)*: Nama mata kuliah
- `-d, --day` *(Wajib)*: Hari kuliah (`Senin` s/d `Minggu`)
- `--start` *(Wajib)*: Jam mulai (format `HH:MM`)
- `--end` *(Wajib)*: Jam selesai (format `HH:MM`)
- `-b, --building` *(Opsional)*: Gedung kelas (contoh: `Gedung C`)
- `-r, --room` *(Opsional)*: Ruang kelas (contoh: `C301`)
- `--notes` *(Opsional)*: Catatan khusus / perlengkapan yang perlu dibawa

**Contoh:**
```bash
mabaops schedule add -c IF102 -n "Struktur Data" -d Senin --start 09:00 --end 10:40 -b "Gedung C" -r "C301" --notes "Bawa laptop"
```

### 3.2 `mabaops schedule list`
Menampilkan tabel jadwal kuliah lengkap dengan opsi filter hari.

**Contoh:**
```bash
# Tampilkan semua jadwal
mabaops schedule list

# Tampilkan jadwal hari Senin saja
mabaops schedule list -d Senin
```

### 3.3 `mabaops schedule today`
Menampilkan jadwal kuliah khusus untuk hari saat command dijalankan (menggunakan nama hari sistem lokal dalam Bahasa Indonesia).

---

## 4. Hasil Pengujian (Testing)

### 4.1 Pytest Suite
Pengujian dijalankan pada virtual environment lokal:
```powershell
& .venv\Scripts\python.exe -m pytest tests
```

**Hasil:**
```txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk
configfile: pyproject.toml
collected 8 items

tests\test_cli.py ........                                               [100%]

============================== 8 passed in 1.05s ==============================
```

**Daftar Test yang Berjalan:**
1. `test_help_shows_mabaops` (Verifikasi help global dan ketersediaan subcommand)
2. `test_init_demo_creates_data_files` (Verifikasi inisialisasi file data demo)
3. `test_today_without_data_prompts_init` (Verifikasi pesan onboarding saat data kosong)
4. `test_today_with_demo_data_outputs_dashboard` (Verifikasi tampilan dashboard ringkas)
5. `test_schedule_add_and_list` (Verifikasi penambahan jadwal dan penampilan tabel list)
6. `test_schedule_list_filters_by_day` (Verifikasi filter jadwal per hari tertentu)
7. `test_schedule_today_with_demo_data_outputs_today_schedule` (Verifikasi pembacaan jadwal hari ini)
8. `test_schedule_add_rejects_invalid_day` (Verifikasi validasi penolakan input hari yang salah)

---

### 4.2 Smoke Test CLI
Verifikasi interaktif langsung melalui binary executable CLI:
- `mabaops schedule --help` → **PASS** (Menampilkan deskripsi subcommands: add, list, today)
- `mabaops schedule list` → **PASS** (Menampilkan Rich Table dengan kolom Hari, Jam, Kode, Mata Kuliah, Lokasi, Catatan)
- `mabaops schedule today` → **PASS** (Menampilkan kelas yang terjadwal untuk hari ini)

---

## 5. Next Step: Plan 3 (Task Manager & Priority Engine)

Modul berikutnya yang siap dieksekusi:
- Subcommand `mabaops task add`, `mabaops task list`, `mabaops task done`.
- Priority scoring otomatis (perhitungan skor urgensi berdasarkan deadline & estimasi durasi).
- Label status: `[URGENT]` (< 48 jam), `[OVERDUE]`, `[OK]`.
- Integrasi top priority tasks ke `mabaops today`.