"""
Web App - Word to PDF Converter
Flask backend: upload .docx/.doc, convert, download PDF.
"""

import os
import uuid
import threading
from pathlib import Path
from flask import (
    Flask, render_template, request,
    send_file, jsonify,
)
from werkzeug.utils import secure_filename

# Import converter from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from converter import convert_file

# -- Config --
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
OUTPUT_FOLDER = Path(__file__).parent / "outputs"
ALLOWED_EXTENSIONS = {".doc", ".docx"}
MAX_FILE_SIZE_MB = 20

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# In-memory job tracker {job_id: {"status", "filename", "pdf_path", "error"}}
jobs: dict = {}
jobs_lock = threading.Lock()


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def convert_job(job_id: str, input_path: str, output_path: str):
    """Background thread: convert and update job status."""
    try:
        convert_file(input_path, output_path)
        with jobs_lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["pdf_path"] = output_path
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
    finally:
        try:
            os.remove(input_path)
        except Exception:
            pass


# -- Routes --

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Hanya file .doc dan .docx yang diizinkan"}), 400

    job_id = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    stem = Path(safe_name).stem
    input_path = UPLOAD_FOLDER / f"{job_id}_{safe_name}"
    output_path = OUTPUT_FOLDER / f"{job_id}_{stem}.pdf"

    file.save(str(input_path))

    with jobs_lock:
        jobs[job_id] = {
            "status": "processing",
            "filename": stem,
            "pdf_path": None,
            "error": None,
        }

    t = threading.Thread(
        target=convert_job,
        args=(job_id, str(input_path), str(output_path)),
        daemon=True,
    )
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job tidak ditemukan"}), 404
    return jsonify({
        "status": job["status"],
        "filename": job["filename"],
        "error": job.get("error"),
    })


@app.route("/download/<job_id>")
def download(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or job["status"] != "done":
        return "File belum siap atau tidak ditemukan", 404

    pdf_path = job["pdf_path"]
    filename = job["filename"] + ".pdf"

    def remove_after_send(path):
        try:
            os.remove(path)
        except Exception:
            pass

    response = send_file(
        pdf_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )
    threading.Thread(target=remove_after_send, args=(pdf_path,), daemon=True).start()
    with jobs_lock:
        jobs.pop(job_id, None)

    return response


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": f"File terlalu besar. Maksimum {MAX_FILE_SIZE_MB} MB"}), 413


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
