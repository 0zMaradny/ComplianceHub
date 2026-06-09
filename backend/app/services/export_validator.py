"""Pre-export validation — last quality gate before document generation.

Runs AFTER the AI router returns a result but BEFORE the document is
exported to DOCX / PDF / Excel. Blocks export if quality is too low
and provides actionable feedback for the user.
"""

import logging

from .ai.debugger import Autodebugger
from .ai.model_registry import FIELD_MIN_LENGTHS, FIELD_MIN_ITEMS

logger = logging.getLogger(__name__)

# ISO terminology for quality checking
ISO_TERMS = {
    "nonconformity", "conformant", "audit evidence", "audit criteria",
    "audit findings", "corrective action", "preventive action", "ofi",
    "opportunity for improvement", "management review", "internal audit",
    "risk assessment", "risk treatment", "statement of applicability",
    "interested parties", "context of the organization", "leadership",
    "continual improvement", "process approach", "pdca",
    "non-conformant", "nonconformity", "observation", "audit programme",
    "audit plan", "audit report", "certification", "surveillance",
    "recertification", "scope of audit", "audit objectives",
}

# Minimum quality score to allow export
EXPORT_MIN_SCORE = 5.0
EXPORT_WARN_SCORE = 7.0


class ExportValidator:
    """Validates AI output quality before document export."""

    def __init__(self, task_type: str):
        self.task_type = task_type
        self.debugger = Autodebugger(task_type)

    def validate(self, ai_output: dict) -> tuple[bool, list[str], float]:
        """
        Validate AI output before export.

        Returns:
            (is_valid, issues, quality_score)
            - is_valid: True if quality_score >= EXPORT_MIN_SCORE
            - issues: list of human-readable issue descriptions
            - quality_score: 0.0 to 10.0
        """
        score, issues = self._score(ai_output)
        is_valid = score >= EXPORT_MIN_SCORE
        if not is_valid:
            logger.warning(
                "[export_validator] BLOCKED %s — score %.1f < %.1f: %s",
                self.task_type, score, EXPORT_MIN_SCORE, issues[:3],
            )
        return is_valid, issues, score

    def get_quality_report(self, ai_output: dict, model_used: str = "") -> dict:
        """
        Generate a detailed quality report for the UI.

        Returns:
            {
                "overall_score": 8.5,
                "structure_pass": true,
                "content_depth_pass": true,
                "item_counts_pass": false,
                "terminology_pass": true,
                "issues": ["positive_findings has 2 items, minimum is 3"],
                "recommendations": ["Regenerate with a stronger model"],
                "model_used": "nemotron_ultra",
                "can_export": true,
                "warnings": ["Content depth below recommended threshold"]
            }
        """
        score, issues = self._score(ai_output)
        warnings = [i for i in issues if "below" in i.lower() or "brief" in i.lower()]

        # Determine which checks passed
        structure_errors = [i for i in issues if "missing" in i.lower() or "required" in i.lower()]
        depth_errors = [i for i in issues if "too short" in i.lower() or "brief" in i.lower() or "fewer than" in i.lower()]
        count_errors = [i for i in issues if "items" in i.lower() and "minimum" in i.lower()]
        term_errors = [i for i in issues if "terminology" in i.lower() or "iso" in i.lower()]

        recommendations = []
        if score < EXPORT_MIN_SCORE:
            recommendations.append("Regenerate with a stronger model (frontier tier)")
            recommendations.append("Add more detail to short fields")
        elif score < EXPORT_WARN_SCORE:
            recommendations.append("Consider regenerating for better quality")
        if structure_errors:
            recommendations.append("Fix missing required fields before export")
        if count_errors:
            recommendations.append("Add more items to meet minimum counts")

        return {
            "overall_score": round(score, 1),
            "structure_pass": len(structure_errors) == 0,
            "content_depth_pass": len(depth_errors) == 0,
            "item_counts_pass": len(count_errors) == 0,
            "terminology_pass": len(term_errors) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "model_used": model_used,
            "can_export": score >= EXPORT_MIN_SCORE,
            "warnings": warnings,
        }

    def _score(self, ai_output: dict) -> tuple[float, list[str]]:
        """Score output quality 0-10. Returns (score, issues)."""
        issues: list[str] = []
        score = 0.0

        # ── 1. Structure check (3 points) ──────────────────────────────
        output_errors = self.debugger.validate_output(ai_output)
        if not output_errors:
            score += 3.0
        else:
            issues.extend(output_errors)

        # ── 2. Content depth check (2 points) ──────────────────────────
        min_lengths = FIELD_MIN_LENGTHS.get(self.task_type, {})
        depth_failures = 0
        for field, min_len in min_lengths.items():
            val = ai_output.get(field)
            if isinstance(val, str) and len(val.strip()) < min_len:
                issues.append(
                    f"'{field}' too short ({len(val.strip())} chars, min {min_len})"
                )
                depth_failures += 1
        if not min_lengths or depth_failures == 0:
            score += 2.0
        elif depth_failures <= len(min_lengths) / 2:
            score += 1.0

        # ── 3. Item count check (2 points) ─────────────────────────────
        min_items = FIELD_MIN_ITEMS.get(self.task_type, {})
        count_failures = 0
        for field, min_count in min_items.items():
            val = ai_output.get(field)
            if isinstance(val, list) and len(val) < min_count:
                issues.append(
                    f"'{field}' has {len(val)} items, minimum {min_count} expected"
                )
                count_failures += 1
        if not min_items or count_failures == 0:
            score += 2.0
        elif count_failures <= len(min_items) / 2:
            score += 1.0

        # ── 4. Placeholder check (2 points) ────────────────────────────
        PLACEHOLDER_PATTERNS = [
            '[Client Name]', '[TBD]', '[Insert', '[Company]',
            '[Name]', '[Date]', '[Location]', '[Address]',
            'TBD', 'tbd', 'N/A', 'n/a', 'TODO', 'todo',
            'lorem ipsum', 'Lorem Ipsum',
        ]
        placeholder_count = 0
        for key, value in ai_output.items():
            if isinstance(value, str):
                for pat in PLACEHOLDER_PATTERNS:
                    if pat.lower() in value.lower():
                        issues.append(f"Placeholder '{pat}' found in '{key}'")
                        placeholder_count += 1
                        break
        if placeholder_count == 0:
            score += 2.0
        elif placeholder_count <= 2:
            score += 1.0

        # ── 5. ISO terminology check (1 point) ─────────────────────────
        term_count = 0
        for key, value in ai_output.items():
            if isinstance(value, str):
                lower_val = value.lower()
                for term in ISO_TERMS:
                    if term in lower_val:
                        term_count += 1
        if term_count >= 3:
            score += 1.0
        elif term_count >= 1:
            score += 0.5
        else:
            issues.append("No ISO audit terminology detected — output may be too generic")

        return min(score, 10.0), issues
