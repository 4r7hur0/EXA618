from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

from flask import Flask, jsonify, redirect, render_template, request
from redis import Redis
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@dataclass(frozen=True)
class Post:
    author: str
    message: str
    created_at: str


_redis_client: Redis | None = None


def _redis() -> Redis:
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    url = os.environ.get("REDIS_URL", "").strip()
    if not url:
        raise RuntimeError(
            "REDIS_URL não configurado. Configure uma instância Redis (ex.: Upstash) e defina a env var REDIS_URL."
        )

    _redis_client = Redis.from_url(url, decode_responses=True)
    return _redis_client


def _messages_key() -> str:
    return os.environ.get("REDIS_MESSAGES_KEY", "atividade21:messages")


def _messages_limit() -> int:
    raw = os.environ.get("REDIS_MESSAGES_LIMIT", "").strip()
    if not raw:
        return 500
    try:
        value = int(raw)
    except ValueError:
        return 500
    return max(1, min(value, 5000))


def _read_posts() -> List[Post]:
    posts: List[Post] = []

    items = _redis().lrange(_messages_key(), 0, -1)
    for item in items:
        try:
            obj = json.loads(item)
        except json.JSONDecodeError:
            continue

        author = str(obj.get("author", "")).strip()
        message = str(obj.get("message", ""))
        created_at = str(obj.get("created_at", "")).strip()
        if not (author and message and created_at):
            continue
        posts.append(Post(author=author, message=message, created_at=created_at))

    return posts


def _append_post(author: str, message: str) -> str:
    created_at = datetime.now().isoformat(timespec="seconds")

    value = json.dumps(
        {"author": author, "message": message, "created_at": created_at},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    r = _redis()
    key = _messages_key()
    pipe = r.pipeline(transaction=True)
    pipe.lpush(key, value)
    pipe.ltrim(key, 0, _messages_limit() - 1)
    pipe.execute()

    return created_at


def _clean_author(value: str) -> str:
    return " ".join(value.strip().split())


def _clean_message(value: str) -> str:
    # Preserve newlines for display; just normalize Windows line endings.
    return value.replace("\r\n", "\n").strip()


@app.get("/")
def index_get():
    try:
        posts = _read_posts()
        return render_template(
            "index.html", posts=posts, error=None, form={"author": "", "message": ""}
        )
    except RuntimeError as e:
        return render_template(
            "index.html",
            posts=[],
            error=str(e),
            form={"author": "", "message": ""},
        )


@app.post("/")
def index_post():
    author = _clean_author(request.form.get("author", ""))
    message = _clean_message(request.form.get("message", ""))

    try:
        posts = _read_posts()
    except RuntimeError as e:
        return (
            render_template(
                "index.html",
                posts=[],
                error=str(e),
                form={"author": author, "message": message},
            ),
            500,
        )

    if not author or not message:
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
    try:
        posts = _read_posts()
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
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

    try:
        created_at = _append_post(author, message)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
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

