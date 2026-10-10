"""Generate closed-model images for one group. Resumable; API keys come only from environment variables.

Usage:
  python gen_closed.py <group> --dry-run          # list jobs and settings, no API calls
  python gen_closed.py <group> --limit 2          # smoke test: 2 images
  python gen_closed.py <group>                    # full run (24 x 16 main + 6 x 16 control = 480 images)
"""
import argparse, base64, csv, datetime, os, sys, time, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from prompts import jobs  # noqa: E402
from config import GROUPS, N_CONTROL, N_MAIN, OUT  # noqa: E402

FIELDS = ["job", "kind", "category", "subject", "prompt", "k", "group", "provider", "model", "params",
          "returned_model", "revised_prompt", "request_id", "utc", "seconds", "file"]


def client_for(G):
    key = os.environ.get(G["key_env"])
    if not key:
        sys.exit(f"missing environment variable {G['key_env']}")
    if G["provider"] == "openai":
        from openai import OpenAI
        c = OpenAI(api_key=key)

        def call(prompt):
            r = c.images.generate(model=G["model"], prompt=prompt, **G["params"])
            d = r.data[0]
            return (base64.b64decode(d.b64_json), getattr(r, "model", "") or "",
                    getattr(d, "revised_prompt", "") or "", getattr(r, "_request_id", "") or "")
    elif G["provider"] == "gemini":
        from google import genai
        c = genai.Client(api_key=key)

        def call(prompt):
            r = c.interactions.create(model=G["model"], input=prompt,
                                      response_format=dict(type="image", **G["params"]))
            return base64.b64decode(r.output_image.data), G["model"], "", getattr(r, "id", "") or ""
    elif G["provider"] == "ark":
        from volcenginesdkarkruntime import Ark
        c = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=key)

        def call(prompt):
            r = c.images.generate(model=G["model"], prompt=prompt, **G["params"])
            d = r.data[0]
            img = base64.b64decode(d.b64_json) if getattr(d, "b64_json", None) else urllib.request.urlopen(d.url).read()
            return img, getattr(r, "model", "") or "", getattr(d, "revised_prompt", "") or "", getattr(r, "id", "") or ""
    else:
        sys.exit(f"unknown provider {G['provider']}")
    return call


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("group", choices=sorted(GROUPS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between requests")
    a = ap.parse_args()

    G = GROUPS[a.group]
    out_dir = f"{OUT}/{a.group}"
    meta_path = f"{out_dir}/meta.csv"
    done = set()
    if os.path.exists(meta_path):
        with open(meta_path, newline="", encoding="utf-8") as f:
            done = {r["job"] for r in csv.DictReader(f)}
    todo = [j for j in jobs(N_MAIN, N_CONTROL) if j["job"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{a.group}: model={G['model']} params={G['params']} todo={len(todo)} done={len(done)} -> {out_dir}")
    if a.dry_run:
        for j in todo[:5] + (["..."] if len(todo) > 5 else []):
            print("  ", j)
        return

    call = client_for(G)
    os.makedirs(out_dir, exist_ok=True)
    new = not os.path.exists(meta_path)
    with open(meta_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        for n, j in enumerate(todo):
            for attempt in range(6):
                try:
                    t = time.time()
                    img, rmodel, revised, rid = call(j["prompt"])
                    break
                except Exception as e:  # rate limits, transient errors; content refusals are logged and skipped
                    print(f"  {j['job']} attempt {attempt}: {type(e).__name__}: {str(e)[:200]}", flush=True)
                    time.sleep(min(120, 10 * 2 ** attempt))
            else:
                print(f"  {j['job']} FAILED, skipped (rerun to retry)", flush=True)
                continue
            fn = f"{j['job']}.png"
            with open(f"{out_dir}/{fn}", "wb") as g:
                g.write(img)
            w.writerow(dict(job=j["job"], kind=j["kind"], category=j["category"], subject=j["subject"],
                            prompt=j["prompt"], k=j["k"], group=a.group, provider=G["provider"], model=G["model"],
                            params=repr(G["params"]), returned_model=rmodel, revised_prompt=revised, request_id=rid,
                            utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                            seconds=round(time.time() - t, 2), file=fn))
            f.flush()
            print(f"{a.group} {n+1}/{len(todo)} {j['job']}", flush=True)
            time.sleep(a.sleep)


if __name__ == "__main__":
    main()
