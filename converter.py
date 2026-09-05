"""
Word to PDF Converter
Converts .doc and .docx files to PDF using multiple backend options.
"""

import os
import sys
import argparse
import platform
from pathlib import Path


def convert_with_docx2pdf(input_path: str, output_path: str) -> bool:
    """Convert using docx2pdf (requires Microsoft Word on Windows/macOS)."""
    try:
        from docx2pdf import convert
        convert(input_path, output_path)
        return True
    except ImportError:
        print("[docx2pdf] Package not installed. Run: pip install docx2pdf")
        return False
    except Exception as e:
        print(f"[docx2pdf] Error: {e}")
        return False


def convert_with_libreoffice(input_path: str, output_dir: str) -> bool:
    """Convert using LibreOffice (cross-platform, headless)."""
    import subprocess
    import shutil

    libreoffice_cmds = ["libreoffice", "libreoffice7.6", "soffice"]

    cmd_found = None
    for cmd in libreoffice_cmds:
        if shutil.which(cmd):
            cmd_found = cmd
            break

    if not cmd_found:
        print("[LibreOffice] LibreOffice is not installed or not in PATH.")
        return False

    try:
        result = subprocess.run(
            [
                cmd_found,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                input_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True
        else:
            print(f"[LibreOffice] Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[LibreOffice] Conversion timed out.")
        return False
    except Exception as e:
        print(f"[LibreOffice] Error: {e}")
        return False


def convert_with_pypandoc(input_path: str, output_path: str) -> bool:
    """Convert using pypandoc (requires pandoc installed)."""
    try:
        import pypandoc
        pypandoc.convert_file(input_path, "pdf", outputfile=output_path)
        return True
    except ImportError:
        print("[pypandoc] Package not installed. Run: pip install pypandoc")
        return False
    except Exception as e:
        print(f"[pypandoc] Error: {e}")
        return False


def convert_file(
    input_path: str,
    output_path: str = None,
    backend: str = "auto",
) -> str:
    """
    Convert a Word file to PDF.

    Args:
        input_path: Path to the .doc or .docx file.
        output_path: Destination PDF path (optional). Defaults to same folder.
        backend: Conversion backend – 'auto', 'docx2pdf', 'libreoffice', 'pypandoc'.

    Returns:
        Path to the generated PDF, or raises RuntimeError on failure.
    """
    input_path = Path(input_path).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() not in (".doc", ".docx"):
        raise ValueError(f"Unsupported file type: {input_path.suffix}")

    # Determine output path
    if output_path is None:
        output_path = input_path.with_suffix(".pdf")
    else:
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_dir = str(output_path.parent)

    print(f"Converting: {input_path.name}  →  {output_path.name}")

    # Backend selection
    success = False

    if backend == "auto":
        # Priority order depends on OS
        if platform.system() in ("Windows", "Darwin"):
            backends = ["docx2pdf", "libreoffice", "pypandoc"]
        else:
            backends = ["libreoffice", "pypandoc", "docx2pdf"]
    else:
        backends = [backend]

    for b in backends:
        print(f"  Trying backend: {b} …")
        if b == "docx2pdf":
            success = convert_with_docx2pdf(str(input_path), str(output_path))
        elif b == "libreoffice":
            # LibreOffice writes <filename>.pdf into output_dir
            success = convert_with_libreoffice(str(input_path), output_dir)
            if success:
                # Rename if needed (LibreOffice uses the source filename)
                generated = Path(output_dir) / (input_path.stem + ".pdf")
                if generated != output_path and generated.exists():
                    generated.rename(output_path)
        elif b == "pypandoc":
            success = convert_with_pypandoc(str(input_path), str(output_path))
        else:
            print(f"  Unknown backend: {b}")
            continue

        if success:
            print(f"  ✓ Done via {b}")
            break

    if not success:
        raise RuntimeError(
            "All backends failed. Install at least one of:\n"
            "  • docx2pdf  (Windows/macOS, needs MS Word)\n"
            "  • LibreOffice  (cross-platform)\n"
            "  • pypandoc  (needs pandoc)"
        )

    return str(output_path)


def batch_convert(
    input_dir: str,
    output_dir: str = None,
    backend: str = "auto",
    recursive: bool = False,
) -> list:
    """
    Convert all Word files in a directory to PDF.

    Returns list of (input_path, output_path, success) tuples.
    """
    input_dir = Path(input_dir).resolve()
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {input_dir}")

    pattern = "**/*.doc*" if recursive else "*.doc*"
    word_files = [
        f for f in input_dir.glob(pattern)
        if f.suffix.lower() in (".doc", ".docx")
    ]

    if not word_files:
        print("No Word files found.")
        return []

    results = []
    for wf in sorted(word_files):
        if output_dir:
            out = Path(output_dir) / wf.relative_to(input_dir).with_suffix(".pdf")
        else:
            out = wf.with_suffix(".pdf")

        try:
            pdf_path = convert_file(str(wf), str(out), backend=backend)
            results.append((str(wf), pdf_path, True))
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results.append((str(wf), None, False))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert Word (.doc/.docx) files to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python converter.py document.docx
  python converter.py document.docx -o output/report.pdf
  python converter.py -d ./docs -o ./pdfs --recursive
  python converter.py document.docx --backend libreoffice
        """,
    )

    parser.add_argument("input", nargs="?", help="Input .docx/.doc file")
    parser.add_argument("-o", "--output", help="Output PDF path")
    parser.add_argument(
        "-d", "--directory",
        help="Convert all Word files in this directory (batch mode)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for batch conversion",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively search subdirectories (batch mode)",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "docx2pdf", "libreoffice", "pypandoc"],
        default="auto",
        help="Conversion backend (default: auto)",
    )

    args = parser.parse_args()

    if args.directory:
        results = batch_convert(
            args.directory,
            output_dir=args.output_dir,
            backend=args.backend,
            recursive=args.recursive,
        )
        total = len(results)
        ok = sum(1 for _, _, s in results if s)
        print(f"\nBatch complete: {ok}/{total} files converted successfully.")
        sys.exit(0 if ok == total else 1)

    elif args.input:
        try:
            pdf = convert_file(args.input, args.output, backend=args.backend)
            print(f"\nOutput: {pdf}")
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
