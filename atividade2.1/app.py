from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from flask import Flask, jsonify, redirect, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@dataclass(frozen=True)
class Post:
    author: str
    message: str
    created_at: str


def _tmp_data_dir() -> Path:
    return Path("/tmp") / "atividade21_blog_data"


def _data_dir() -> Path:
    """Onde gravar o CSV: local `data/`, override por env, ou /tmp em serverless."""
    override = os.environ.get("DATA_DIR", "").strip()
    if override:
        return Path(override)
    # Vercel expõe combinações diferentes conforme runtime/preview.
    if (
        os.environ.get("VERCEL")
        or os.environ.get("VERCEL_ENV")
        or os.environ.get("VERCEL_URL")
    ):
        return _tmp_data_dir()

    local = Path(__file__).resolve().parent / "data"
    try:
        local.mkdir(parents=True, exist_ok=True)
        probe = local / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        return _tmp_data_dir()
    return local


def _csv_path() -> Path:
    return _data_dir() / "messages.csv"


def _ensure_storage_exists() -> None:
    data_dir = _data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    csv_path = _csv_path()
    if csv_path.exists():
        return

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["author", "message", "created_at"])
        writer.writeheader()


def _read_posts() -> List[Post]:
    _ensure_storage_exists()
    posts: List[Post] = []

    with _csv_path().open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            author = (row.get("author") or "").strip()
            message = row.get("message") or ""
            created_at = (row.get("created_at") or "").strip()
            if not (author and message and created_at):
                continue
            posts.append(Post(author=author, message=message, created_at=created_at))

    posts.reverse()
    return posts


def _append_post(author: str, message: str) -> str:
    _ensure_storage_exists()
    created_at = datetime.now().isoformat(timespec="seconds")

    with _csv_path().open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["author", "message", "created_at"])
        writer.writerow({"author": author, "message": message, "created_at": created_at})

    return created_at


def _clean_author(value: str) -> str:
    return " ".join(value.strip().split())


def _clean_message(value: str) -> str:
    # Preserve newlines for display; just normalize Windows line endings.
    return value.replace("\r\n", "\n").strip()


@app.get("/")
def index_get():
    posts = _read_posts()
    return render_template("index.html", posts=posts, error=None, form={"author": "", "message": ""})


@app.post("/")
def index_post():
    author = _clean_author(request.form.get("author", ""))
    message = _clean_message(request.form.get("message", ""))

    if not author or not message:
        posts = _read_posts()
        return (
            render_template(
                "index.html",
                posts=posts,
                error="Preencha autor e mensagem.",
                form={"author": author, "message": message},
            ),
            400,
        )

    if len(author) > 60:
        posts = _read_posts()
        return (
            render_template(
                "index.html",
                posts=posts,
                error="Autor deve ter no máximo 60 caracteres.",
                form={"author": author[:60], "message": message},
            ),
            400,
        )

    if len(message) > 1000:
        posts = _read_posts()
        return (
            render_template(
                "index.html",
                posts=posts,
                error="Mensagem deve ter no máximo 1000 caracteres.",
                form={"author": author, "message": message[:1000]},
            ),
            400,
        )

    _append_post(author, message)
    # Evita url_for em serverless (SCRIPT_NAME / rotas reescritas podem quebrar o redirect).
    return redirect("/", code=303)


@app.get("/api/messages")
def api_messages_get():
    posts = _read_posts()
    return jsonify(
        {
            "messages": [
                {"author": p.author, "message": p.message, "created_at": p.created_at}
                for p in posts
            ]
        }
    )


@app.post("/api/messages")
def api_messages_post():
    payload = request.get_json(silent=True) or {}

    action = str(payload.get("action", "")).strip()
    author = _clean_author(str(payload.get("author", "")))
    message = _clean_message(str(payload.get("message", "")))

    if not action:
        return jsonify({"error": 'Campo obrigatório: action (use "put")'}), 400

    if action != "put":
        return jsonify({"error": 'action inválida (use "put")'}), 400

    if not author or not message:
        return jsonify({"error": "Campos obrigatórios: author, message"}), 400

    if len(author) > 60:
        return jsonify({"error": "author deve ter no máximo 60 caracteres"}), 400

    if len(message) > 1000:
        return jsonify({"error": "message deve ter no máximo 1000 caracteres"}), 400

    created_at = _append_post(author, message)
    return (
        jsonify(
            {
                "ok": True,
                "action": action,
                "message": {"author": author, "message": message, "created_at": created_at},
            }
        ),
        201,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    # On Render (and most hosts) the web service must bind to 0.0.0.0 and the PORT env var.
    # Debug should be off in production; use `gunicorn app:app`.
    app.run(host="0.0.0.0", port=port, debug=False)

