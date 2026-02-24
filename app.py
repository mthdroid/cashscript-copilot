#!/usr/bin/env python3
"""
CashScript Copilot - AI-Powered CashScript Development Assistant
An intelligent tool for generating, auditing, explaining, and optimizing
CashScript smart contracts on Bitcoin Cash.

Usage:
    python app.py                # Start on http://localhost:5050
    python app.py --port 8080    # Custom port
"""

import argparse
import json
import os
import logging
from pathlib import Path

from flask import Flask, render_template, request, jsonify

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ai_engine import AIEngine
from cashscript_knowledge import EXAMPLE_CONTRACTS

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cashscript-copilot-dev-key")

log = logging.getLogger("copilot")

# Lazy-init AI engine (only when first request comes in)
_engine = None

def get_engine() -> AIEngine:
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main page with the Copilot interface."""
    examples = {
        name: {"name": ex["name"], "description": ex["description"]}
        for name, ex in EXAMPLE_CONTRACTS.items()
    }
    return render_template("index.html", examples=examples)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate a CashScript contract from description."""
    data = request.get_json()
    description = data.get("description", "").strip()
    if not description:
        return jsonify({"error": "Description is required"}), 400

    try:
        engine = get_engine()
        result = engine.generate(description)
        return jsonify(result)
    except Exception as e:
        log.error(f"Generate error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/audit", methods=["POST"])
def api_audit():
    """Audit a CashScript contract."""
    data = request.get_json()
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"error": "Code is required"}), 400

    try:
        engine = get_engine()
        result = engine.audit(code)
        return jsonify(result)
    except Exception as e:
        log.error(f"Audit error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/explain", methods=["POST"])
def api_explain():
    """Explain a CashScript contract."""
    data = request.get_json()
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"error": "Code is required"}), 400

    try:
        engine = get_engine()
        result = engine.explain(code)
        return jsonify(result)
    except Exception as e:
        log.error(f"Explain error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    """Optimize a CashScript contract."""
    data = request.get_json()
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"error": "Code is required"}), 400

    try:
        engine = get_engine()
        result = engine.optimize(code)
        return jsonify(result)
    except Exception as e:
        log.error(f"Optimize error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Free-form chat about CashScript."""
    data = request.get_json()
    message = data.get("message", "").strip()
    history = data.get("history", [])
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        engine = get_engine()
        result = engine.chat(message, history)
        return jsonify(result)
    except Exception as e:
        log.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/example/<name>")
def api_example(name: str):
    """Get example contract code."""
    ex = EXAMPLE_CONTRACTS.get(name)
    if not ex:
        return jsonify({"error": f"Unknown example: {name}"}), 404
    return jsonify({
        "name": ex["name"],
        "description": ex["description"],
        "code": ex["code"],
    })


@app.route("/api/health")
def api_health():
    """Health check endpoint."""
    has_key = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
    return jsonify({
        "status": "ok",
        "provider": os.getenv("AI_PROVIDER", "anthropic"),
        "api_key_configured": has_key,
    })


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description="CashScript Copilot")
    parser.add_argument("--port", type=int, default=None, help="Port (default: 5050)")
    parser.add_argument("--host", default=None, help="Host (default: 127.0.0.1)")
    parser.add_argument("--production", action="store_true", help="Run with waitress (production)")
    args = parser.parse_args()

    # PORT env var takes priority (used by Railway/Render), then CLI arg, then default
    port = int(os.getenv("PORT", 0)) or args.port or 5050
    host = args.host or os.getenv("HOST", "127.0.0.1")
    production = args.production or os.getenv("PRODUCTION", "").lower() in ("1", "true")

    provider = os.getenv("AI_PROVIDER", "anthropic")
    has_key = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    print()
    print("  CASHSCRIPT COPILOT")
    print(f"  http://{host}:{port}")
    print(f"  AI Provider: {provider}")
    print(f"  API Key: {'configured' if has_key else 'MISSING - set ANTHROPIC_API_KEY or OPENAI_API_KEY'}")
    print()

    if production:
        from waitress import serve
        print("  Running with Waitress (production)")
        serve(app, host=host, port=port)
    else:
        app.run(host=host, port=port, debug=True)
