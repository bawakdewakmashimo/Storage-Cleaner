# Storage Cleaner & Audit Utility

Utilitas audit dan pembersih penyimpanan folder berbasis **Node.js** native (`fs`, `path`, `crypto`, `readline`, `os`) tanpa dependensi eksternal (`npm install` tidak diperlukan). Skrip ini memindai folder target secara rekursif, mendeteksi file raksasa (> 2 MB), mengidentifikasi file duplikat berdasarkan hash SHA-256 identik, dan menyediakan pembersihan interaktif.

Tersedia juga alternatif berbasis **Python 3** (`os`, `hashlib`, `sys`, `pathlib`) dengan fungsionalitas identik.

---

## 🚀 Fitur Utama

- **Pemindaian Rekursif Mendalam**: Memindai seluruh direktori dan subdirektori secara otomatis.
- **Deteksi Hash SHA-256 Identik**: Mengelompokkan file dengan konten identik meskipun memiliki nama berbeda (misalnya `modul.pdf` dan `modul_BACKUP.pdf`).
- **Penandaan File Raksasa**: Mengidentifikasi file berukuran ≥ 2 MB (2.048 KB).
- **Terminal UI Responsif & Elegan**: Dilengkapi layout border box, indikator progres real-time, badge status, dan format ukuran bytes (B, KB, MB, GB).
- **Pembersihan Interaktif Cerdas**: Menanyakan konfirmasi `(Y/N)` sebelum menghapus. Mempertahankan 1 file asli dan hanya menghapus salinan redundan serta file sampah `.tmp`.
- **Zero Dependencies**: Berjalan langsung menggunakan runtime Node.js bawaan tanpa `npm install`.

---

## 💻 Cara Menjalankan

### 1. Node.js (Utama)

Jalankan langsung melalui terminal / PowerShell:

```bash
# Menjalankan audit interaktif (default otomatis mencari Downloads_Lab)
node storage_audit.js

# Menjalankan audit dalam mode simulasi / pratinjau (tanpa menghapus file)
node storage_audit.js --dry-run

# Menjalankan audit dengan target folder kustom
node storage_audit.js "C:\Users\Student\Downloads\Downloads_Lab"

# Membuka Web UI Dashboard visual lokal (Port 3000)
node storage_audit.js --web
```

### 2. Python (Alternatif)

Jika runtime Python terpasang di sistem:

```bash
python storage_audit.py
# atau dengan dry-run:
python storage_audit.py --dry-run
```

---

## 📊 Hasil Audit Contoh (`Downloads_Lab`)

- **Total File**: 64 file (61.41 MB)
- **File Raksasa (≥ 2 MB)**: 15 file
- **Kelompok Duplikat**: 20 kelompok (21 salinan redundant)
- **Potensi Hemat Ruang**: ~18.00 MB