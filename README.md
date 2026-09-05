# Word to PDF Converter

Aplikasi untuk mengonversi file `.doc` dan `.docx` ke PDF.
Tersedia sebagai **desktop app** (drag & drop) dan **CLI**.

---

## Untuk Pengguna Umum (tanpa install Python)

### Download .exe langsung

1. Buka halaman **[Releases](https://github.com/Ajisuryoalam/word-to-pdf/releases)**
2. Download file **`WordToPDF.exe`** dari versi terbaru
3. Double-click – langsung bisa dipakai, tidak perlu install apapun

> **Catatan:** Anda tetap perlu menginstall salah satu backend konversi:
> - **Windows:** Install [Microsoft Word](https://www.microsoft.com/microsoft-365) atau [LibreOffice](https://www.libreoffice.org/download/)
> - **Linux/macOS:** Install [LibreOffice](https://www.libreoffice.org/download/)

---

## Untuk Developer (clone & run)

### 1. Clone repo

```bash
git clone https://github.com/Ajisuryoalam/word-to-pdf.git
cd word-to-pdf
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install backend konversi (pilih salah satu)

| Backend | Platform | Cara Install |
|---|---|---|
| `docx2pdf` | Windows/macOS | `pip install docx2pdf` + MS Word |
| LibreOffice | Semua | [libreoffice.org](https://www.libreoffice.org) |
| `pypandoc` | Semua | `pip install pypandoc` + `pypandoc.download_pandoc()` |

### 4. Jalankan

```bash
# Desktop GUI (drag & drop)
python gui_app.py

# CLI – satu file
python converter.py laporan.docx

# CLI – seluruh folder
python converter.py -d ./dokumen -o ./hasil
```

---

## Build .exe Sendiri

```powershell
# Windows PowerShell
.\build_exe.ps1
```

File `.exe` akan tersimpan di folder `dist\WordToPDF.exe`.

---

## Fitur

- Drag & drop file `.docx` / `.doc`
- Konversi batch (banyak file sekaligus)
- Pilih folder output
- Progress bar per file
- CLI & Python API
- Otomatis pilih backend terbaik yang tersedia

---

## Menjalankan Tests

```bash
pytest tests/ -v
```

---

## Lisensi

MIT License – lihat [LICENSE](LICENSE)
