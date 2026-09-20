# Report 4 — Comprehensive Security, PRD Alignment & Engineering Quality Audit

Tanggal: 2026-09-20  
Lokasi project: `C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk`

---

## 1. Ringkasan Eksekutif

Audit komprehensif telah dijalankan terhadap seluruh codebase **MabaOps** di `Projek_Ngantuk` dengan standar keamanan, kualitas kode (*High-Performance Engineering*), dan kesesuaian dokumen spesifikasi produk (**PRD-MabaOps.md**).

### Skor & Status Pengujian
- **Pytest Suite:** **28 passed** (meningkat dari 24 passed, 100% lulus dalam ~4.8s).
- **Security Check:** Zero hardcoded secrets, subprocess environment isolation aktif, Windows atomic write locked retry aktif, report path traversal sanitized.
- **PRD Alignment:** Data model sinkron 100% dengan PRD Bab 12, milestone MVP 1-6 terpenuhi, command `schedule delete` dan `task plan` heuristic aktif, demo test case & sample solution tersedia out-of-the-box.
- **CLI & UX:** Inset formatting bug `Rp: Rp` pada `budget summary` diperbaiki, multi-week budget leakage pada `today` & `dashboard` diperbaiki.

---

## 2. Temuan & Tindakan Perbaikan (Action Matrix)

| Kategori | ID | Temuan Awal | Tingkat Risiko | Tindakan & Status Perbaikan |
|---|---|---|---|---|
| **Keamanan** | **S1** | Subprocess `assessor.py` mewarisi seluruh environment variabel parent host (risiko token/API key bocor ke script student). | Sedang-Tinggi | **SELESAI:** Diisolasi menggunakan `safe_env` minimal (`SYSTEMROOT`, `PATH`, `PATHEXT`, `TEMP`, `TMP`, `PYTHONIOENCODING`). |
| **Keamanan** | **S2** | Potensi hardcoded secret, token API, atau private key pada codebase. | Kritis | **AUDITED - AMAN:** Tidak ditemukan secret/token hardcoded. File `.env.example` hanya placeholder komentar; `.gitignore` mencakup `.env*`. |
| **Keamanan** | **S3** | `write_json` berpotensi error `PermissionError` [WinError 5/32] saat atomic replace file JSON jika file sedang dibaca proses Windows lain (misal antivirus/indexing). | Sedang | **SELESAI:** Ditambahkan mekanisme retry loop 5x dengan delay 50ms untuk atomic replace pada Windows. |
| **Keamanan** | **S4** | File report markdown pada `assessor.py` berpotensi path traversal jika nama file/label mengandung karakter khusus (`../`). | Rendah-Sedang | **SELESAI:** Ditambahkan sanitasi nama label dengan regex `re.sub(r"[^a-zA-Z0-9_-]", "_", ...)`. |
| **Logika Bisnis** | **B1** | `mabaops today` dan `mabaops dashboard` menjumlahkan seluruh entri budget sepanjang masa (*all-time*), bukan per minggu berjalan, sehingga terjadi defisit palsu di minggu ke-2 dst. | Kritis | **SELESAI:** Disinkronkan dengan `budget_summary()`, sehingga perhitungan spent dan remaining konsisten murni untuk minggu berjalan. |
| **Formatting / UX** | **B2** | Output `mabaops budget summary` menduplikasi prefix mata uang: `Rp: Rp 500.000`. | Rendah (Visual) | **SELESAI:** `format_rupiah` diperbaiki agar mendukung label kosong tanpa redundansi prefix. |
| **Logika Bisnis** | **B3** | Filter minggu `budget_summary` hanya `>= monday` tanpa batas atas `< next_monday`, berisiko entri masa depan/data uji bocor ke minggu aktif. | Sedang | **SELESAI:** Dibatasi rentang mingguan eksplisit `monday <= entry_dt < next_monday`. |
| **PRD Alignment** | **P1** | Model data `models.py` belum memuat field PRD Bab 12: `CourseSchedule.lecturer`, `TaskItem.description`, `TaskItem.category`, `TaskItem.subtasks`, dan model `AssessmentReport`. | Sedang | **SELESAI:** Seluruh field dan model ditambahkan dengan default value backwards-compatible. |
| **PRD Alignment** | **P2** | Command PRD Bab 8 `mabaops schedule delete` dan `mabaops task plan` belum tersedia di CLI. | Sedang | **SELESAI:** Diimplementasikan di CLI dan storage (`schedule delete <code|id>` dan `task plan <id>` heuristic breakdown). |
| **PRD Alignment / Demo** | **P4** | README menyertakan contoh `mabaops assess solution.py --cases test_cases/array`, tetapi foldernya belum ada di repo. | Sedang | **SELESAI:** Dibuat folder `test_cases/array/` (`case1.in/out`, `case2.in/out`) dan `solution.py`. Pengujian demo berjalan 100% lulus. |

---

## 3. Detail Verifikasi Pengujian

### 3.1 Otomasi Unit & Integration Test (`pytest`)

Dijalankan via RTK runner di lingkungan virtual `.venv`:
```powershell
rtk .venv\Scripts\pytest.exe tests
```

Hasil:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Swift 3\Documents\PROJEK\Projek_Ngantuk
configfile: pyproject.toml
collected 28 items

tests\test_cli.py ............................                           [100%]

============================= 28 passed in 4.80s ==============================
```

Daftar 4 test baru yang ditambahkan:
1. `test_schedule_delete`: Memvalidasi penghapusan jadwal kuliah berdasarkan kode MK dan list menjadi kosong.
2. `test_task_plan_heuristic`: Memvalidasi pembagian tugas besar menjadi micro-tasks terstruktur dan tersimpan di `subtasks`.
3. `test_budget_summary_clean_currency_formatting`: Memvalidasi format tabel `budget summary` bebas dari bug `Rp: Rp`.
4. `test_today_budget_isolates_previous_week_entries`: Memvalidasi isolasi pengeluaran minggu lalu agar tidak mengurangi budget minggu berjalan pada `today`.

---

### 3.2 Smoke Test CLI Live

1. **`mabaops budget summary`**:
   Tabel rapi tanpa glitch formatting:
   ```text
   +---------------------------------------+
   | Budget mingguan          | Rp 500.000 |
   | Pemasukan (minggu ini)   |       Rp 0 |
   | Pengeluaran (minggu ini) |  Rp 15.000 |
   | Sisa                     | Rp 485.000 |
   | Rata-rata per hari       |   Rp 2.142 |
   | Proyeksi akhir minggu    |  Rp 14.999 |
   | Sisa hari di minggu ini  |          0 |
   +---------------------------------------+
   ```

2. **`mabaops task plan <id>`**:
   Menghasilkan langkah kerja actionable untuk mahasiswa baru:
   ```text
   Rencana pengerjaan (Actionable Micro-tasks): Tugas Array (ID: 1072e242)
     -> 1. Pahami soal & analisis test cases (15m)
     -> 2. Implementasi struktur data & logika utama (45m)
     -> 3. Uji edge cases & running test (.in/.out) (30m)
     -> 4. Refactor kode & periksa rubrik pengumpulan (15m)
   ```

3. **`mabaops assess solution.py --cases test_cases/array`**:
   ```text
         Assessment: solution.py       
   +----------------------------------+
   | Case  | Status | Durasi | Detail |
   |-------+--------+--------+--------|
   | case1 | passed |   77ms | -      |
   | case2 | passed |   77ms | -      |
   +----------------------------------+
   Skor: 100 (2/2 passed, 0 failed, 0 timeout, 0 error)
   ```

---

## 4. Status Dokumen & Roadmap

- `README.md`: Diperbarui dengan badge **28 passed**, dokumentasi command `schedule delete`, `task plan`, dan referensi file demo test case.
- `docs/ROADMAP.md`: Item `schedule delete` dan `task plan` heuristic ditandai selesai.
- `pyproject.toml`: Konfigurasi package, scripts, dan pytest tetap valid dan bersih.
