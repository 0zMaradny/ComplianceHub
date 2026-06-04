import time
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

MAX_SELF_HEAL_RETRIES = 2

PLACEHOLDER_PATTERNS = [
    '[Client Name]', '[TBD]', '[Insert', '[Company]',
    '[Name]', '[Date]', '[Location]', '[Address]',
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
    ],
    'TNL': [
        ('client_name', str), ('audit_date', str), ('standard', str),
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

    def call_with_self_heal(self, provider_fn, prompt: str,
                            system_prompt: str | None = None,
                            **kwargs) -> dict[str, Any]:
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
