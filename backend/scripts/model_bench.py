"""Model bench - rank models per doc type by quality/time.

Runs the full router.generate pipeline (rate-limit, health, PII scrub,
tier fallback, caching) for every model in the registry, then prints
a sorted table of quality vs latency.

Usage:
    python -m scripts.model_bench           # bench all 21 models vs Audit_Report
    python -m scripts.model_bench TNL     # bench one doc type
    python -m scripts.model_bench --top 3 # show top-3 per doc type
"""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.ai.router import _try_provider
from app.services.ai.model_registry import ALL_MODELS
from app.services.ai_pipeline import _build_prompt

NOTES = "Evidence verified across clauses 4-10. Risk register maintained."
MANDAY = "Total Mandays: 6 | Lead (3), Auditor (3)."


def _bench_one(name: str, doc_type: str, api_key: str) -> dict:
    """Run _try_provider for one model; return a plain dict suitable for the table."""
    prompt = _build_prompt(NOTES, MANDAY, ["ISO 9001:2015"], doc_type)
    t0 = time.perf_counter()
    r, err = _try_provider(name, doc_type, prompt, api_key=api_key, mode="generate")
    ms = int((time.perf_counter() - t0) * 1000)
    if r is None or "error" in r:
        return {"model": name, "ok": False,
                "quality": 0, "ms": ms,
                "error": (err or "")[:80]}
    quality = r.get("_quality_score", 0) if isinstance(r, dict) else 0
    return {"model": name, "ok": True, "quality": quality, "ms": ms}


def main():
    ap = argparse.ArgumentParser(description="Rank models by quality/time")
    ap.add_argument("doc_type", nargs="?", default="Audit_Report",
                    help="ISO doc type to benchmark against")
    ap.add_argument("--models", default="",
                    help="Comma-separated list of model names to bench (overrides default)")
    ap.add_argument("--top", type=int, default=1,
                    help="Show only this many rows per doc type")
    a = ap.parse_args()

    # Determine which models to benchmark
    if a.models:
        names = [m.strip() for m in a.models.split(",") if m.strip()]
        # Validate that named models exist in registry
        names = [n for n in names if n in ALL_MODELS]
    else:
        # Default: ALL models in the registry (PREMIUM + FRONTIER + STRONG + GROQ + LOCAL)
        names = list(ALL_MODELS.keys())

    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    rows = []
    for name in names:
        row = _bench_one(name, a.doc_type, api_key)
        rows.append(row)

    # Sort: highest quality first, then lowest latency
    rows.sort(key=lambda x: (-x.get("quality", 0), x.get("ms", 999999)))

    # Print a compact table
    prefix = f"\n== Model Bench: {a.doc_type} (top {a.top}) =="
    print(prefix)
    print(f"{'model':<18}{'ok':<5}{'quality':<9}{'ms'}")
    for r in rows[:a.top]:
        ok_s = "yes" if r.get("ok") else "no"
        q = r.get("quality", "-")
        m = r.get("ms", "-")
        print(f"{r['model']:<18}{ok_s:<5}{q:<9}{m}")

    failed = [r for r in rows if not r.get("ok")]
    if failed:
        print("\nFailures:")
        for r in failed:
            print(f"  {r['model']}: {r.get('error')}")

    # Persist raw results
    out_path = os.path.join(os.path.dirname(__file__), "bench_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()