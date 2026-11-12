import os
from flask import Flask, render_template, request
from hashlib import sha256
from urllib.parse import urlparse

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan-file", methods=["POST"])
def scan_file():
    file = request.files.get("file")

    if not file or not file.filename:
        return render_template(
            "index.html",
            error="Lütfen bir dosya seç."
        )

    file_hash = sha256(file.stream.read()).hexdigest()

    return render_template(
        "index.html",
        result={
            "name": file.filename,
            "hash": file_hash,
            "status": "Analiz bekliyor"
        }
    )


@app.route("/scan-url", methods=["POST"])
def scan_url():
    url = request.form.get("url", "").strip()
    parsed = urlparse(url)

    valid = (
        parsed.scheme in ("http", "https")
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
    )

    if not valid:
        return render_template(
            "index.html",
            error="Geçerli bir HTTP veya HTTPS adresi gir."
        )

    return render_template(
        "index.html",
        url_result=url,
        url_status="URL biçimi geçerli. Tehdit taraması henüz yapılmadı."
    )


@app.errorhandler(413)
def too_large(error):
    return render_template(
        "index.html",
        error="Dosya boyutu 20 MB sınırını aşıyor."
    ), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)