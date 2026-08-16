"""Verify _provider_has_key works for Groq registry keys (groq_llama, groq_scout)."""
import sys, os
sys.path.insert(0, "C:/Users/eos/ComplianceHub/backend")
from app.services.ai.router import _provider_has_key

# These should return True when GROQ_API_KEY is present
ok = True
results = {}
for key in ["groq", "groq_llama", "groq_scout"]:
    val = _provider_has_key(key)
    results[key] = val
    if not val:
        ok = False

print("Groq key detection results:")
for k, v in results.items():
    print(f"  {k}: {v}")

if ok:
    print("\nAll Groq keys detected successfully.")
else:
    print("\nSome Groq keys were NOT detected.")
    sys.exit(1)