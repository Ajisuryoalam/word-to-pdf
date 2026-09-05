"""
Word to PDF Converter - Desktop GUI
Drag & drop atau browse file .docx/.doc, lalu konversi ke PDF.

Requirements:
    pip install tkinterdnd2
"""

import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from converter import convert_file


# Colours
BG        = "#1e1e2e"
SURFACE   = "#2a2a3d"
ACCENT    = "#7c3aed"
ACCENT_LT = "#a855f7"
TEXT      = "#e2e8f0"
MUTED     = "#94a3b8"
SUCCESS   = "#22c55e"
ERROR     = "#ef4444"
WARN      = "#f59e0b"


class DropZone(tk.Frame):
    def __init__(self, master, on_drop, **kwargs):
        super().__init__(master, bg=SURFACE, **kwargs)
        self._on_drop = on_drop
        self._canvas = tk.Canvas(self, bg=SURFACE, highlightthickness=0, width=440, height=180)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.create_text(220, 65, text="DRAG & DROP", font=("Segoe UI", 28), fill=TEXT)
        self._canvas.create_text(220, 110, text="file .docx / .doc ke sini", font=("Segoe UI", 12), fill=MUTED)
        self._canvas.create_text(220, 138, text="atau klik tombol Pilih File di bawah", font=("Segoe UI", 9), fill=MUTED)
        self._draw_border()
        if DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._handle_drop)

    def _draw_border(self, color=ACCENT):
        self._canvas.delete("border")
        self._canvas.create_rectangle(6, 6, 434, 174, outline=color, dash=(8, 4), width=2, tags="border")

    def _handle_drop(self, event):
        import re
        raw = event.data.strip()
        paths = [p[0] or p[1] for p in re.findall(r"\{([^}]+)\}|(\S+)", raw)]
        self._on_drop(paths)


class FileRow(tk.Frame):
    def __init__(self, master, filepath, on_remove, **kwargs):
        super().__init__(master, bg=SURFACE, **kwargs)
        self.filepath = filepath
        self._sv = tk.StringVar(value="Menunggu...")

        name = Path(filepath).name
        tk.Label(self, text="[DOC]", bg=SURFACE, fg=ACCENT_LT, font=("Consolas", 9, "bold")).pack(side="left", padx=(8,4))
        tk.Label(self, text=name, bg=SURFACE, fg=TEXT, font=("Segoe UI", 10), anchor="w", width=28).pack(side="left", fill="x", expand=True)
        self._lbl = tk.Label(self, textvariable=self._sv, bg=SURFACE, fg=MUTED, font=("Segoe UI", 9))
        self._lbl.pack(side="left", padx=8)
        tk.Button(self, text="X", bg=SURFACE, fg=ERROR, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), command=lambda: on_remove(self)).pack(side="right", padx=4)
        tk.Frame(master, bg="#3a3a50", height=1).pack(fill="x", padx=8)

    def set_status(self, text, color=MUTED):
        self._sv.set(text)
        self._lbl.configure(fg=color)


BaseApp = TkinterDnD.Tk if DND_AVAILABLE else tk.Tk


class App(BaseApp):
    def __init__(self):
        super().__init__()
        self.title("Word to PDF Converter")
        self.geometry("500x640")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._rows = []
        self._outdir = ""
        self._build()

    def _build(self):
        # Header
        h = tk.Frame(self, bg=ACCENT, height=52)
        h.pack(fill="x")
        tk.Label(h, text="  Word to PDF Converter", bg=ACCENT, fg="white",
                 font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", padx=12, pady=10)

        # Drop zone
        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="x", padx=20, pady=16)
        self._dz = DropZone(pad, on_drop=self._add_files)
        self._dz.pack(fill="x")

        if not DND_AVAILABLE:
            tk.Label(pad, text="Install tkinterdnd2 untuk drag & drop", bg=BG, fg=WARN, font=("Segoe UI", 9)).pack(pady=4)

        # Buttons
        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=20, pady=6)
        tk.Button(bf, text="Pilih File (.docx)", command=self._browse, bg=ACCENT, fg="white",
                  relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"), padx=12, pady=7).pack(side="left", padx=(0,6))
        tk.Button(bf, text="Folder Output", command=self._browse_out, bg=SURFACE, fg=TEXT,
                  relief="flat", cursor="hand2", font=("Segoe UI", 10), padx=12, pady=7).pack(side="left")

        self._lbl_out = tk.Label(self, text="Output: sama dengan file sumber",
                                  bg=BG, fg=MUTED, font=("Segoe UI", 9), anchor="w")
        self._lbl_out.pack(fill="x", padx=20)

        # File list
        tk.Label(self, text="File yang dipilih:", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", padx=20, pady=(10,2))
        self._lf = tk.Frame(self, bg=SURFACE)
        self._lf.pack(fill="both", expand=True, padx=20)
        self._empty = tk.Label(self._lf, text="Belum ada file", bg=SURFACE, fg=MUTED, font=("Segoe UI", 10))
        self._empty.pack(pady=20)

        # Progress
        self._prog = ttk.Progressbar(self, mode="determinate")
        self._prog.pack(fill="x", padx=20, pady=8)

        # Convert btn
        self._btn = tk.Button(self, text="Konversi Sekarang", command=self._convert,
                               bg=ACCENT, fg="white", relief="flat", cursor="hand2",
                               font=("Segoe UI", 12, "bold"), pady=12)
        self._btn.pack(fill="x", padx=20, pady=4)

        # Status
        self._sv = tk.StringVar(value="Siap")
        tk.Label(self, textvariable=self._sv, bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(pady=4)

    def _browse(self):
        paths = filedialog.askopenfilenames(filetypes=[("Word", "*.docx *.doc")])
        if paths:
            self._add_files(list(paths))

    def _browse_out(self):
        d = filedialog.askdirectory()
        if d:
            self._outdir = d
            self._lbl_out.configure(text=f"Output: {d}", fg=ACCENT_LT)

    def _add_files(self, paths):
        existing = {r.filepath for r in self._rows}
        for p in paths:
            p = p.strip().strip("{}")
            if not p or Path(p).suffix.lower() not in (".doc", ".docx") or p in existing:
                continue
            row = FileRow(self._lf, p, self._remove)
            row.pack(fill="x", pady=2, padx=4)
            self._rows.append(row)
            existing.add(p)
        self._refresh()

    def _remove(self, row):
        self._rows.remove(row)
        row.destroy()
        self._refresh()

    def _refresh(self):
        if self._rows:
            self._empty.pack_forget()
            self._sv.set(f"{len(self._rows)} file siap")
        else:
            self._empty.pack(pady=20)
            self._sv.set("Siap")

    def _convert(self):
        if not self._rows:
            messagebox.showinfo("Info", "Pilih file .docx terlebih dahulu.")
            return
        self._btn.configure(state="disabled", text="Mengonversi...")
        self._prog["maximum"] = len(self._rows)
        self._prog["value"] = 0
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        ok = 0
        for i, row in enumerate(self._rows):
            row.set_status("Proses...", WARN)
            self._sv.set(f"Mengonversi {i+1}/{len(self._rows)}...")
            try:
                out = None
                if self._outdir:
                    out = str(Path(self._outdir) / (Path(row.filepath).stem + ".pdf"))
                convert_file(row.filepath, out)
                row.set_status("SELESAI", SUCCESS)
                ok += 1
            except Exception as e:
                row.set_status(f"GAGAL: {str(e)[:30]}", ERROR)
            self._prog["value"] = i + 1
            self.update_idletasks()

        total = len(self._rows)
        self._btn.configure(state="normal", text="Konversi Sekarang")
        if ok == total:
            self._sv.set(f"Semua {total} file berhasil!")
            messagebox.showinfo("Selesai!", f"{total} file berhasil dikonversi ke PDF.")
        else:
            self._sv.set(f"{ok} berhasil, {total-ok} gagal")
            messagebox.showwarning("Selesai", f"{ok}/{total} file berhasil.")


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
