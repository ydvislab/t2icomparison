"""Serve the built audit tool and store the in-tool aspect checks.

Usage: python serve.py [--port 8772] [--bind 127.0.0.1]
- Serves $T2IC_DATA/audit_tool/ (the output of build.py) as static files.
- /api/ping            GET  -> {"ok": true}; the page uses it to know that checks can be stored on the server.
- /api/checks          GET  -> all stored check runs (JSON list); POST -> append one run (JSON object), returns its id.
- /api/checks.csv      GET  -> the same runs as CSV, one row per judged pair.
Check runs are appended to $T2IC_DATA/audit_store/checks.jsonl (one JSON object per line; never rewritten). They hold
the analyst's initials and judgements, so they stay outside git (CLAUDE.md: no raw personal annotation exports).
"""
import argparse, csv, io, json, os, threading, time, uuid
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
ROOT = os.path.join(DATA, "audit_tool")
STORE = os.path.join(DATA, "audit_store", "checks.jsonl")
LOCK = threading.Lock()
MAX_BODY = 512 * 1024


def read_runs():
    if not os.path.exists(STORE):
        return []
    with open(STORE, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript", ".wasm": "application/wasm",
                      ".js": "text/javascript", ".onnx": "application/octet-stream"}

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/ping":
            return self._json({"ok": True})
        if path == "/api/checks":
            with LOCK:
                return self._json(read_runs())
        if path == "/api/checks.csv":
            with LOCK:
                runs = read_runs()
            out = io.StringIO(); w = csv.writer(out)
            w.writerow(["run_id", "time", "annotator", "aspect", "left_pole", "right_pole", "members", "run", "pair", "subject",
                        "left_image", "right_image", "clip_side", "answer", "agree_run", "cant_tell_run", "pass_run"])
            for r in runs:
                a = r.get("aspect", {})
                for i, p in enumerate(r.get("pairs") or [{}] * len(r.get("answers", []))):
                    w.writerow([r.get("id"), r.get("time"), r.get("annotator", ""), a.get("name"), a.get("left"), a.get("right"),
                                " ".join(r.get("members", [])), r.get("run"), i + 1, p.get("subject", ""),
                                "/".join(p.get("L", ["", ""])), "/".join(p.get("R", ["", ""])), p.get("clip", ""),
                                (r.get("answers") or [""] * (i + 1))[i], r.get("agree"), r.get("cant"), r.get("pass")])
            b = out.getvalue().encode("utf-8-sig")
            self.send_response(200); self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=aspect_checks.csv")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            return
        return super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/checks":
            return self._json({"ok": False, "error": "not found"}, 404)
        n = int(self.headers.get("Content-Length") or 0)
        if not 0 < n <= MAX_BODY:
            return self._json({"ok": False, "error": "empty or too large"}, 400)
        try:
            rec = json.loads(self.rfile.read(n).decode("utf-8"))
            assert isinstance(rec, dict) and isinstance(rec.get("aspect"), dict) and isinstance(rec.get("answers"), list)
        except Exception:
            return self._json({"ok": False, "error": "not a check run"}, 400)
        with LOCK:
            known = {r.get("client_id") for r in read_runs()}
            if rec.get("client_id") and rec["client_id"] in known:   # a retried upload: keep the first copy
                rid = next(r["id"] for r in read_runs() if r.get("client_id") == rec["client_id"])
                return self._json({"ok": True, "id": rid, "duplicate": True})
            rec["id"] = uuid.uuid4().hex[:12]
            rec["received"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            os.makedirs(os.path.dirname(STORE), exist_ok=True)
            with open(STORE, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return self._json({"ok": True, "id": rec["id"]})

    def end_headers(self):
        if self.path.endswith((".html", "/")) or "data.js" in self.path:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main():
    global STORE
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8772); ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--root", default=ROOT, help="folder with the built tool (default $T2IC_DATA/audit_tool; '.' inside an offline package)")
    ap.add_argument("--store", default=None, help="file for the check runs (default $T2IC_DATA/audit_store/checks.jsonl, or <root>/checks.jsonl with --root)")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    STORE = os.path.abspath(a.store) if a.store else (STORE if root == os.path.abspath(ROOT) else os.path.join(root, "checks.jsonl"))
    srv = ThreadingHTTPServer((a.bind, a.port), partial(Handler, directory=root))
    print(f"serving {root} on http://{a.bind}:{a.port}/ ; checks -> {STORE}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
