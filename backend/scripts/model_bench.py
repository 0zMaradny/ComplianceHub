"""Model bench - rank models per doc type by quality/time. Requires OPENROUTER_API_KEY."""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.ai.router import _try_provider
from app.services.ai.model_registry import ALL_MODELS
from app.services.ai_pipeline import _build_prompt

NOTES = "Evidence verified across clauses 4-10. Risk register maintained."
MANDAY = "Total Mandays: 6 | Lead (3), Auditor (3)."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc_type", nargs="?", default="Audit_Report")
    ap.add_argument("--models", default="")
    ap.add_argument("--top", type=int, default=1)
    a = ap.parse_args()
    names = [m.strip() for m in a.models.split(",") if m.strip()] if a.models else \
        [n for n, m in ALL_MODELS.items() if m.provider == "openrouter"]
    prompt = _build_prompt(NOTES, MANDAY, ["ISO 9001:2015"], a.doc_type)
    rows = []
    for name in names:
        t0 = time.perf_counter()
        r, err = _try_provider(name, a.doc_type, prompt, api_key=os.environ.get("OPENROUTER_API_KEY", ""), mode="generate")
        ms = int((time.perf_counter() - t0) * 1000)
        rows.append({"model": name, "ok": r is not None and "error" not in r,
                     "quality": (r or {}).get("_quality_score", 0), "ms": ms,
                     "error": (err or "")[:80]} if r is None or "error" in r
                    else {"model": name, "ok": True, "quality": r.get("_quality_score", 0), "ms": ms})
    rows.sort(key=lambda x: (-x.get("quality", 0), x.get("ms", 999999)))
    print(f"\n== Model Bench: {a.doc_type} (top {a.top}) ==")
    print(f"{'model':<15}{'ok':<5}{'quality':<9}{'ms'}")
    for r in rows[:a.top]:
        print(f"{r['model']:<15}{str(r.get('ok')):<5}{r.get('quality', '-'):<9}{r.get('ms', '-')}")
    failed = [r for r in rows if not r.get("ok")]
    if failed:
        print("\nFailures:")
        for r in failed:
            print(f"  {r['model']}: {r.get('error')}")
    with open(os.path.join(os.path.dirname(__file__), "bench_results.json"), "w") as f:
        json.dump(rows[:a.top], f, indent=2)

if __name__ == "__main__":
    main()