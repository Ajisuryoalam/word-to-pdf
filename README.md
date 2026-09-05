# 📄 Word to PDF Converter

> Convert `.doc` and `.docx` files to PDF from the command line or import as a Python library.

---

## ✨ Features

- **Single file** or **batch directory** conversion
- **Multiple backends** — automatically picks the best one available:
  | Backend | Platform | Requires |
  |---|---|---|
  | `docx2pdf` | Windows / macOS | Microsoft Word |
  | `libreoffice` | Linux / macOS / Windows | LibreOffice |
  | `pypandoc` | Cross-platform | Pandoc binary |
- **Recursive** directory scanning
- Clean CLI with helpful flags
- Importable Python API

---

## 🚀 Installation

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/word-to-pdf.git
cd word-to-pdf
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install a conversion backend

Choose **one or more**:

#### Option A – `docx2pdf` (Windows / macOS, needs Microsoft Word)

```bash
pip install docx2pdf
```

#### Option B – LibreOffice (cross-platform, recommended for Linux)

```bash
# Ubuntu / Debian
sudo apt install libreoffice

# macOS
brew install --cask libreoffice

# Windows: download from https://www.libreoffice.org/
```

#### Option C – pypandoc (needs Pandoc)

```bash
pip install pypandoc
# Install pandoc binary:
python -c "import pypandoc; pypandoc.download_pandoc()"
```

---

## 🖥️ Usage

### Single file

```bash
python converter.py report.docx
python converter.py report.docx -o output/report.pdf
```

### Batch conversion (entire folder)

```bash
python converter.py -d ./documents -o ./pdfs
python converter.py -d ./documents --recursive
```

### Choose a specific backend

```bash
python converter.py report.docx --backend libreoffice
python converter.py report.docx --backend docx2pdf
python converter.py report.docx --backend pypandoc
```

### All options

```
usage: converter.py [-h] [-o OUTPUT] [-d DIRECTORY] [--output-dir OUTPUT_DIR]
                    [-r] [--backend {auto,docx2pdf,libreoffice,pypandoc}]
                    [input]

Arguments:
  input                    Input .docx/.doc file
  -o, --output             Output PDF path
  -d, --directory          Batch: convert all Word files in this directory
  --output-dir             Output directory for batch mode
  -r, --recursive          Recurse into subdirectories
  --backend                Backend to use (default: auto)
```

---

## 🐍 Python API

```python
from converter import convert_file, batch_convert

# Single file
pdf_path = convert_file("report.docx")
pdf_path = convert_file("report.docx", output_path="out/report.pdf", backend="libreoffice")

# Batch
results = batch_convert("./docs", output_dir="./pdfs", recursive=True)
for src, dst, ok in results:
    print(f"{'✓' if ok else '✗'} {src} → {dst}")
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📋 Requirements

- Python **3.8+**
- At least one conversion backend (see above)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.
