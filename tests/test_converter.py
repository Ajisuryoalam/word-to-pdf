"""
Tests for the Word-to-PDF converter.
Uses tmp_path fixtures and mocking so no real Word install is needed.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_docx(path: Path) -> Path:
    """Create a minimal .docx file (just touches it – backends are mocked)."""
    path.write_bytes(b"PK\x03\x04")  # ZIP magic bytes
    return path


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestConvertFile:
    def test_file_not_found(self, tmp_path):
        from converter import convert_file
        with pytest.raises(FileNotFoundError):
            convert_file(str(tmp_path / "ghost.docx"))

    def test_unsupported_extension(self, tmp_path):
        from converter import convert_file
        f = tmp_path / "doc.txt"
        f.write_text("hello")
        with pytest.raises(ValueError, match="Unsupported file type"):
            convert_file(str(f))

    def test_default_output_path(self, tmp_path):
        """Output defaults to same directory as input with .pdf extension."""
        from converter import convert_file
        docx = make_docx(tmp_path / "report.docx")

        with patch("converter.convert_with_docx2pdf", return_value=True) as m:
            result = convert_file(str(docx), backend="docx2pdf")

        assert result.endswith("report.pdf")
        m.assert_called_once()

    def test_custom_output_path(self, tmp_path):
        from converter import convert_file
        docx = make_docx(tmp_path / "report.docx")
        out = tmp_path / "out" / "final.pdf"

        with patch("converter.convert_with_docx2pdf", return_value=True):
            result = convert_file(str(docx), str(out), backend="docx2pdf")

        assert result == str(out.resolve())

    def test_all_backends_fail_raises(self, tmp_path):
        from converter import convert_file
        docx = make_docx(tmp_path / "report.docx")

        with patch("converter.convert_with_docx2pdf", return_value=False), \
             patch("converter.convert_with_libreoffice", return_value=False), \
             patch("converter.convert_with_pypandoc", return_value=False):
            with pytest.raises(RuntimeError, match="All backends failed"):
                convert_file(str(docx), backend="auto")

    def test_fallback_to_second_backend(self, tmp_path):
        from converter import convert_file
        docx = make_docx(tmp_path / "report.docx")

        with patch("converter.convert_with_libreoffice", return_value=False), \
             patch("converter.convert_with_pypandoc", return_value=True):
            result = convert_file(str(docx), backend="auto")

        assert result.endswith(".pdf")


class TestBatchConvert:
    def test_empty_directory(self, tmp_path):
        from converter import batch_convert
        results = batch_convert(str(tmp_path))
        assert results == []

    def test_converts_all_docx(self, tmp_path):
        from converter import batch_convert
        for name in ["a.docx", "b.docx", "c.doc"]:
            make_docx(tmp_path / name)

        with patch("converter.convert_file", side_effect=lambda i, o, **kw: o) as m:
            results = batch_convert(str(tmp_path), backend="docx2pdf")

        assert len(results) == 3
        assert all(ok for _, _, ok in results)

    def test_not_a_directory_raises(self, tmp_path):
        from converter import batch_convert
        with pytest.raises(NotADirectoryError):
            batch_convert(str(tmp_path / "no_such_dir"))

    def test_recursive_finds_nested(self, tmp_path):
        from converter import batch_convert
        sub = tmp_path / "sub"
        sub.mkdir()
        make_docx(sub / "nested.docx")

        with patch("converter.convert_file", side_effect=lambda i, o, **kw: o):
            results = batch_convert(str(tmp_path), recursive=True)

        assert len(results) == 1


class TestBackends:
    def test_docx2pdf_missing_package(self, tmp_path):
        from converter import convert_with_docx2pdf
        with patch.dict("sys.modules", {"docx2pdf": None}):
            result = convert_with_docx2pdf("x.docx", "x.pdf")
        assert result is False

    def test_libreoffice_not_in_path(self, tmp_path):
        from converter import convert_with_libreoffice
        with patch("shutil.which", return_value=None):
            result = convert_with_libreoffice("x.docx", str(tmp_path))
        assert result is False

    def test_libreoffice_success(self, tmp_path):
        from converter import convert_with_libreoffice
        make_docx(tmp_path / "x.docx")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/libreoffice"), \
             patch("subprocess.run", return_value=mock_result):
            ok = convert_with_libreoffice(str(tmp_path / "x.docx"), str(tmp_path))

        assert ok is True

    def test_pypandoc_missing_package(self):
        from converter import convert_with_pypandoc
        with patch.dict("sys.modules", {"pypandoc": None}):
            result = convert_with_pypandoc("x.docx", "x.pdf")
        assert result is False
