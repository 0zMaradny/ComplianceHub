# humanizer — Anti-Slop Skill for OWL
**Version:** 1.0 | **Owner:** Agent 2 + Agent 5 | **Runs BEFORE:** Skill 21 → Skill 22

## Purpose
Remove AI writing patterns before delivery. Based on Wikipedia's "Signs of AI writing."

## 33 Patterns to Remove
1-5: Inflated symbolism, overwrought metaphors, promotional superlatives, grandiose scope, buzzword stacking
6-10: Em dash overuse, forced rule of three, "Not just X but Y", "Indeed"/"Moreover" starts, lists where prose works
11-20: AI vocab: delve, navigate, landscape, foster, pivotal, nuanced, comprehensive→full, robust→strong, seamless→smooth, streamline→simplify
21-27: Vague attribution, hedging overload, sycophantic openings, unearned certainty, restate-in-conclusion, excessive bolding, "Moving on to..."
28-33: "In conclusion"/"In summary", "It's important to note", "At the end of the day", parenthetical-asides, semicolon chains, Oxford comma inconsistencies

## NEVER Modify
- Code blocks, formulas (V=S×(1−U/4), L×S, L×I), ISO clause refs (A.5.24), doc codes (MSD-MOI-GRC-), technical terms, Arabic RTL structure

## Pipeline Position
Content Generation → humanizer → Skill 21 (Language Gate) → Skill 22 (Quality Gates) → Delivery

## Arabic Rules
- Preserve قمنا بـ / تم voice (practitioner, first-person)
- Don't convert to passive bureaucratic Arabic
- Keep ISO refs in English inside Arabic paragraphs

_Last updated: 2026-08-09 · OWL v4.0_
