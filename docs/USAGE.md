# MabaOps — Panduan Penggunaan

Panduan lengkap cara pakai MabaOps dari nol sampai lancar.

---

## 1. Instalasi

```bash
# Clone & install (butuh Python 3.11+)
git clone <repo-url> && cd mabaops
pip install -e .[dev]
```

Cek instalasi:

```bash
mabaops --help
```

---

## 2. Setup Awal

```bash
# Setup dengan data contoh (rekomendasi untuk pertama kali)
mabaops init --demo

# Atau mulai kosong
mabaops init
```

Hasilnya akan ada 4 file di folder `data/`:

| File | Isi |
|---|---|
| `schedule.json` | Jadwal kuliah |
| `tasks.json` | Tugas & deadline |
| `budget.json` | Konfigurasi budget mingguan |
| `budget_entries.json` | Catatan pemasukan/pengeluaran |

> Data disimpan lokal (local-first). Tidak perlu login, tidak perlu internet.

---

## 3. Dashboard Harian

Ini command yang paling sering dipakai:

```bash
mabaops today        # ringkasan teks: jadwal hari ini, top deadline, budget, saran fokus
mabaops dashboard    # TUI 3-panel: Jadwal | Deadline Prioritas | Budget (+ progress bar)
```

`today` menjawab: *"Hari ini aku harus ngapain?"* — tugas dengan skor prioritas tertinggi muncul paling atas.

---

## 4. Kelola Jadwal Kuliah

### Tambah jadwal

```bash
mabaops schedule add \
  -c IF101 \
  -n "Algoritma dan Pemrograman" \
  -d Senin \
  --start 08:00 --end 10:30 \
  -b "Gedung A" -r "A201" \
  --notes "Naik tangga kiri, datang 10 menit lebih awal"
```

| Flag | Arti |
|---|---|
| `-c` | Kode mata kuliah |
| `-n` | Nama mata kuliah |
| `-d` | Hari (Senin–Minggu; alias dikenali: `jum'at`, `ahad`, dll.) |
| `--start` / `--end` | Jam mulai/selesai `HH:MM` |
| `-b` / `-r` | Gedung / ruangan (opsional) |
| `--notes` | Catatan rute/persiapan (opsional) |

### Lihat jadwal

```bash
mabaops schedule list            # semua jadwal
mabaops schedule list -d Kamis   # filter per hari
mabaops schedule today           # hanya jadwal hari ini
```

---

## 5. Kelola Tugas & Deadline

### Tambah tugas

```bash
mabaops task add "Tugas Array" --due 2026-09-25 --estimate 120 --course IF101
```

| Flag | Arti |
|---|---|
| `--due` | Deadline. Format: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM`, atau `YYYY-MM-DDTHH:MM` |
| `--estimate` | Estimasi pengerjaan dalam menit (mempengaruhi prioritas) |
| `--course` | Kode mata kuliah terkait (opsional) |

### Priority otomatis

Setiap tugas langsung diberi label & skor:

| Label | Kondisi | Arti |
|---|---|---|
| `OVERDUE` | Lewat deadline | 🔴 Paling tinggi prioritas |
| `URGENT` | ≤ 48 jam lagi | 🟡 Prioritas tinggi |
| `OK` | > 48 jam | 🟢 Normal |
| `DONE` | Sudah selesai | Tidak muncul di `today` |

### Lihat & update status

```bash
mabaops task list                        # urut dari prioritas tertinggi
mabaops task list --status in_progress   # filter status
mabaops task list --course IF101         # filter mata kuliah

mabaops task start <id>   # mulai kerjakan (in_progress)
mabaops task done <id>    # selesai (done)
```

> `<id>` cukup prefix-nya, misal `a1b2c3d4` dari ID penuh. Copy dari output `task add` atau `task list`.

---

## 6. Kelola Budget Mingguan

### Set budget

```bash
mabaops budget set-weekly 500000
```

### Catat pengeluaran & pemasukan

```bash
mabaops budget add expense 15000 -c makan -n "nasi ayam kantin"
mabaops budget add expense 5000 -c print -n "fotokopi modul"
mabaops budget add income 50000 -n "uang tambahan dari ortu"
```

Kategori expense: `makan`, `transport`, `print`, `organisasi`, `hiburan`, `lain-lain`.
Alias dikenali otomatis: `minum` → makan, `fotokopi` → print, `gojek` → transport, dll.

### Cek ringkasan

```bash
mabaops budget summary
```

Output: total budget, pemasukan, pengeluaran, sisa, rata-rata harian, **proyeksi akhir minggu**, dan status:

- **Aman** — pace masih sesuai budget
- **Perlu perhatian (warning)** — proyeksi akhir minggu melebihi budget
- **Perlu perhatian (deficit)** — pengeluaran sudah melebihi budget

> Summary hanya menghitung entri minggu berjalan (sejak Senin).

---

## 7. Cek Tugas Coding Sebelum Submit

Siapkan test case dalam format `.in`/`.out`:

```text
test_cases/array/
├── case1.in    # input (stdin)
├── case1.out   # output yang diharapkan
├── case2.in
└── case2.out
```

Jalankan:

```bash
mabaops assess solution.py --cases test_cases/array
mabaops assess solution.py --cases test_cases/array --timeout 2
```

Hasil per case:

| Status | Arti |
|---|---|
| `passed` | Output cocok dengan `.out` |
| `failed` | Output beda |
| `timeout` | Program melebihi batas waktu (default 2 detik) |
| `error` | Program crash |

Exit code `1` kalau ada kegagalan — cocok juga buat dipasang di script/pre-commit.
Markdown report otomatis tersimpan di `reports/`.

---

## 8. Web Dashboard (CRUD dari Browser)

Kalau lebih suka klik-klik daripada ngetik command:

```bash
pip install -e .[web]      # sekali saja
mabaops web                # buka http://127.0.0.1:8000
```

Yang bisa dilakukan dari browser:

| Modul | Aksi |
|---|---|
| Jadwal | Lihat semua + jadwal hari ini, tambah matkul, hapus |
| Tugas | Tambah, mulai (`▶`), selesai (`✓`), buka lagi, hapus |
| Budget | Set budget mingguan, catat pemasukan/pengeluaran, hapus entri, lihat riwayat |

Data web dan CLI **sama persis** — sama-sama baca/tulis `data/*.json`. Tambah tugas di web, langsung kelihatan di `mabaops today`, dan sebaliknya.

Server hanya jalan di localhost (127.0.0.1), tidak diakses dari luar. Stop dengan `Ctrl+C`.

---

## 9. Workflow Harian yang Disarankan

```bash
# Pagi sebelum berangkat
mabaops dashboard        # lihat kelas hari ini + deadline bahaya

# Dapat tugas baru dari grup WA
mabaops task add "Laporan Praktikum 3" --due 2026-09-28 --estimate 180 --course IF102

# Mau mulai ngerjain
mabaops task list                     # lihat ID-nya
mabaops task start a1b2c3d4

# Setiap habis jajan
mabaops budget add expense 12000 -c makan -n "ayam geprek"

# Sebelum submit tugas coding
mabaops assess praktikum3.py --cases test_cases/prak3

# Kalau udah selesai
mabaops task done a1b2c3d4
```

---

## 10. Tips & Troubleshooting

**Ganti lokasi data:**
```bash
mabaops today --data-dir ~/.mabaops
# atau set permanen via env var:
export MABAOPS_DATA_DIR=~/.mabaops
```

**Pesan "Belum ada data MabaOps"** → jalankan `mabaops init` dulu.

**Pesan "Budget mingguan belum diset"** → jalankan `mabaops budget set-weekly <jumlah>`.

**Format deadline ditolak** → pakai `YYYY-MM-DD`, contoh: `2026-09-25`.

**Data rusak/corrupt** → file JSON di `data/` bisa diedit manual dengan text editor (formatnya readable).

**`mabaops web` error "Dependensi web belum terinstall"** → jalankan `pip install -e .[web]`.

**Jalankan tests:**
```bash
pytest    # 24 passed
```
