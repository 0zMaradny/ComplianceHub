import time
import json
import logging
from typing import Any

from .model_registry import FIELD_MIN_LENGTHS, FIELD_MIN_ITEMS

logger = logging.getLogger(__name__)

MAX_SELF_HEAL_RETRIES = 2

PLACEHOLDER_PATTERNS = [
    '[Client Name]', '[TBD]', '[Insert', '[Company]',
    '[Name]', '[Date]', '[Location]', '[Address]',
    'TBD', 'tbd', 'N/A', 'n/a', 'TODO', 'todo',
    'lorem ipsum', 'Lorem Ipsum',
]

REQUIRED_FIELDS = {
    'extract_shared_context': [
        ('client_name', str),
    ],
    'Audit_Plan_Stage_1': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('stage', str), ('audit_team', list), ('audit_objectives', list),
        ('audit_scope', str), ('audit_criteria', list), ('daily_schedule', list),
    ],
    'Audit_Plan_Stage_2': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('stage', str), ('audit_team', list), ('audit_objectives', list),
        ('audit_scope', str), ('audit_criteria', list), ('daily_schedule', list),
    ],
    'Participation_List': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('participants', list),
    ],
    'Audit_Report': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('report_number', str), ('scope', str), ('lead_auditor', str),
        ('findings_summary', str), ('conclusion', str),
        ('methodology', dict),
    ],
    'ISO_Checklist': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('sections', list),
    ],
    'Certificate_Text': [
        ('client_name', str), ('certificate_number', str), ('standard', str),
        ('audit_date', str), ('scope', str), ('certification_decision', str),
    ],
    'Certificate': [
        ('client_name', str), ('certificate_number', str), ('standard', str),
        ('audit_date', str), ('scope', str), ('certification_decision', str),
        ('conditions', list),
    ],
    'TNL': [
        ('client_name', str), ('audit_date', str), ('standard', str),
        ('summary', dict),
    ],
}

SCHEDULE_FIELDS = {'day': int, 'date': str, 'time': str, 'activity': str, 'auditee': str, 'auditor': str, 'clause': str}
PARTICIPANT_FIELDS = {'name': str, 'company': str, 'department': str}
SECTION_FIELDS = {'clause': str, 'status': str, 'evidence': str}


class Autodebugger:
    def __init__(self, task_type: str):
        self.task_type = task_type
        self.audit_log: list[dict] = []
        self._log('init', {'task_type': task_type})

    def _log(self, stage: str, details: dict):
        entry = {
            'stage': stage,
            'task_type': self.task_type,
            'timestamp': time.time(),
            **details,
        }
        self.audit_log.append(entry)
        logger.debug('[debugger] %s %s: %s', self.task_type, stage, json.dumps(details, default=str))

    def validate_input(self, prompt: str, **kwargs) -> list[str]:
        errors = []
        if not prompt or len(prompt.strip()) < 10:
            errors.append('Prompt is empty or too short')
        if kwargs.get('system_prompt') and len(kwargs['system_prompt'].strip()) < 5:
            errors.append('System prompt is too short')
        if errors:
            self._log('input_validation_failed', {'errors': errors})
        else:
            self._log('input_validation_passed', {})
        return errors

    def validate_output(self, result: dict) -> list[str]:
        errors = []
        if 'error' in result and result.get('error'):
            errors.append(f"Provider error: {result['error']}")

        req = REQUIRED_FIELDS.get(self.task_type, [])
        for field, expected_type in req:
            val = result.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                errors.append(f"Missing required field '{field}'")
            elif expected_type and not isinstance(val, expected_type):
                errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(val).__name__}")

        for key, value in result.items():
            if isinstance(value, str):
                for pat in PLACEHOLDER_PATTERNS:
                    if pat.lower() in value.lower():
                        errors.append(f"Placeholder '{pat}' found in field '{key}'")
                        break

        if self.task_type in ('Audit_Plan_Stage_1', 'Audit_Plan_Stage_2'):
            for i, entry in enumerate(result.get('daily_schedule', [])):
                for f, ft in SCHEDULE_FIELDS.items():
                    val = entry.get(f)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        errors.append(f"daily_schedule[{i}] missing '{f}'")

        if self.task_type == 'Audit_Report':
            methodology = result.get('methodology', {})
            for sub in ('approach', 'sampling', 'criteria', 'methods'):
                val = methodology.get(sub, '')
                if not val or not val.strip():
                    errors.append(f"methodology.{sub} is empty")

        if self.task_type == 'Certificate':
            conditions = result.get('conditions', [])
            if not isinstance(conditions, list):
                errors.append("conditions must be a list")

        if self.task_type == 'Participation_List':
            for i, p in enumerate(result.get('participants', [])):
                for f in ('name',):
                    if not p.get(f):
                        errors.append(f"participants[{i}] missing '{f}'")

        if self.task_type == 'ISO_Checklist':
            for i, s in enumerate(result.get('sections', [])):
                for f in ('clause', 'status'):
                    if not s.get(f):
                        errors.append(f"sections[{i}] missing '{f}'")

        if not errors:
            self._log('output_validation_passed', {})
        return errors

    def build_corrective_prompt(self, original_prompt: str, errors: list[str]) -> str:
        correction = "\n\n[SYSTEM CORRECTION — The previous output had validation errors. Fix ALL of these:\n"
        for err in errors:
            correction += f"  - {err}\n"
        correction += "\nReturn ONLY valid JSON. Do NOT use placeholder text. Fill every required field.]"
        self._log('corrective_prompt', {'errors': errors})
        return original_prompt + correction

    def validate_quality(self, result: dict) -> list[str]:
        """Quality gate: check that output meets minimum content standards.

        Different from validate_output():
        - validate_output() checks STRUCTURE (fields present, correct types)
        - validate_quality() checks CONTENT (not too short, not generic, enough items)

        Errors here should trigger a RETRY WITH A BETTER MODEL.
        """
        errors: list[str] = []

        # ── Field length checks ──────────────────────────────────────────
        min_lengths = FIELD_MIN_LENGTHS.get(self.task_type, {})
        for field, min_len in min_lengths.items():
            val = result.get(field)
            if isinstance(val, str) and len(val.strip()) < min_len:
                errors.append(
                    f"Quality: '{field}' too short ({len(val.strip())} chars, "
                    f"min {min_len}). Likely generic/placeholder content."
                )

        # ── List item count checks ──────────────────────────────────────
        min_items = FIELD_MIN_ITEMS.get(self.task_type, {})
        for field, min_count in min_items.items():
            val = result.get(field)
            if isinstance(val, list) and len(val) < min_count:
                errors.append(
                    f"Quality: '{field}' has {len(val)} items, "
                    f"minimum {min_count} expected for professional output."
                )

        # ── Nested quality: audit schedule entries must have detail ─────
        if self.task_type in ('Audit_Plan_Stage_1', 'Audit_Plan_Stage_2'):
            for i, entry in enumerate(result.get('daily_schedule', [])):
                activity = entry.get('activity', '')
                if activity and len(activity.strip()) < 20:
                    errors.append(
                        f"Quality: daily_schedule[{i}].activity too brief "
                        f"('{activity}'). Needs specific task description."
                    )
                clause = entry.get('clause', '')
                if clause and not any(c.isdigit() for c in clause):
                    errors.append(
                        f"Quality: daily_schedule[{i}].clause missing "
                        f"clause reference ('{clause}'). Must include ISO clause number."
                    )

        # ── Audit Report: findings must be substantial paragraphs ──────
        if self.task_type == 'Audit_Report':
            summary = result.get('findings_summary', '')
            if summary and summary.count('.') < 4:
                errors.append(
                    "Quality: findings_summary has fewer than 4 sentences. "
                    "Must be 3-5 full paragraphs."
                )
            conclusion = result.get('conclusion', '')
            if conclusion and conclusion.count('.') < 3:
                errors.append(
                    "Quality: conclusion has fewer than 3 sentences. "
                    "Must be 2-3 full paragraphs."
                )
            methodology = result.get('methodology', {})
            if isinstance(methodology, dict):
                for sub in ('approach', 'sampling', 'criteria', 'methods'):
                    val = methodology.get(sub, '')
                    if val and len(val.strip()) < 30:
                        errors.append(
                            f"Quality: methodology.{sub} too brief ({len(val.strip())} chars). "
                            f"Needs full paragraph."
                        )

        # ── ISO_Checklist: evidence must be detailed ────────────────────
        if self.task_type == 'ISO_Checklist':
            sections = result.get('sections', [])
            short_evidence = 0
            for s in sections:
                ev = s.get('evidence', '')
                if ev and len(ev.strip()) < 30:
                    short_evidence += 1
            if sections and short_evidence > len(sections) * 0.5:
                errors.append(
                    f"Quality: {short_evidence}/{len(sections)} checklist items "
                    f"have brief evidence (< 30 chars). Output appears low-effort."
                )

        # ── TNL: descriptions must be detailed ─────────────────────────
        if self.task_type == 'TNL':
            for i, entry in enumerate(result.get('entries', [])):
                desc = entry.get('description', '')
                if desc and len(desc.strip()) < 40:
                    errors.append(
                        f"Quality: TNL entry[{i}].description too brief. "
                        f"Must be 2-3 detailed sentences."
                    )

        if not errors:
            self._log('quality_gate_passed', {})
        else:
            self._log('quality_gate_failed', {'errors': errors})

        return errors

    def build_quality_retry_prompt(self, original_prompt: str, errors: list[str]) -> str:
        """Build a forceful retry prompt for quality failures.
        Used when switching to a better model after quality gate failure."""
        correction = "\n\n[QUALITY RETRY — Previous model produced substandard output.\n"
        correction += "Produce a PROFESSIONAL-GRADE document. Issues:\n"
        for err in errors:
            correction += f"  - {err}\n"
        correction += "\nRules:\n"
        correction += "  - Every evidence/description: 2-3 FULL sentences with specific observations.\n"
        correction += "  - No generic filler. All content must be document-specific and detailed.\n"
        correction += "  - Paragraphs must have 3+ sentences each.\n"
        correction += "  - Return ONLY valid JSON with COMPLETE content.]"
        self._log('quality_retry_prompt', {'errors': errors})
        return original_prompt + correction

    def call_with_self_heal(self, provider_fn, prompt: str,
                            system_prompt: str | None = None,
                            **kwargs) -> dict[str, Any]:
        """Two-phase validation with quality-aware retry.

        Phase 1: Structure (validate_output) → same-model self-heal retry
        Phase 2: Quality (validate_quality) → flags for model upgrade

        Caller should check for '_quality_errors' and retry with next provider.
        """
        input_errors = self.validate_input(prompt, system_prompt=system_prompt, **kwargs)
        if input_errors:
            return {'error': '; '.join(input_errors), '_audit': self.audit_log}

        current_prompt = prompt
        for attempt in range(MAX_SELF_HEAL_RETRIES + 1):
            if attempt > 0:
                self._log('self_heal_retry', {'attempt': attempt})

            call_kwargs = dict(kwargs)
            if system_prompt is not None:
                call_kwargs['system_prompt'] = system_prompt
            result = provider_fn(current_prompt, **call_kwargs)
            self._log('provider_response', {'attempt': attempt, 'has_error': 'error' in result})

            output_errors = self.validate_output(result)
            if not output_errors:
                # Structure passed → now check quality
                quality_errors = self.validate_quality(result)
                if not quality_errors:
                    result['_audit'] = self.audit_log
                    return result
                # Quality failed → return with _quality_errors for model upgrade
                if attempt < MAX_SELF_HEAL_RETRIES:
                    current_prompt = self.build_quality_retry_prompt(prompt, quality_errors)
                    continue
                result['_quality_errors'] = quality_errors
                result['_audit'] = self.audit_log
                return result

            if attempt < MAX_SELF_HEAL_RETRIES:
                current_prompt = self.build_corrective_prompt(prompt, output_errors)
            else:
                self._log('self_heal_exhausted', {'errors': output_errors})
                result['_validation_errors'] = output_errors
                result['_audit'] = self.audit_log
                return result

        return {'error': 'Self-heal exhausted', '_audit': self.audit_log}
