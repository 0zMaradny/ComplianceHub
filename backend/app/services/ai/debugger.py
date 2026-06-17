import time
import json
import logging
from typing import Any

from .model_registry import FIELD_MIN_LENGTHS, FIELD_MIN_ITEMS, MIN_SCORE_THRESHOLDS

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
    'chat_query': [
        ('response', str),
    ],

    'Management_Review_Minutes': [
        ('client_name', str), ('review_date', str), ('standard', str),
        ('chairperson', str), ('attendees', list), ('agenda_items', list),
        ('decisions', list), ('action_items', list), ('review_inputs', str),
        ('review_outputs', str), ('next_review_date', str), ('report_date', str),
    ],
    'Corrective_Action_Report': [
        ('client_name', str), ('car_number', str), ('standard', str),
        ('audit_date', str), ('nc_reference', str), ('clause', str),
        ('severity', str), ('problem_description', str), ('root_cause', str),
        ('containment_actions', list), ('corrective_actions', list),
        ('preventive_actions', list), ('verification_method', str),
        ('status', str), ('reviewed_by', str), ('closure_date', str),
    ],
    'Gap_Analysis_Report': [
        ('client_name', str), ('assessment_date', str), ('standard', str),
        ('assessor', str), ('methodology', str), ('sections', list),
        ('summary', dict), ('overall_assessment', str),
    ],
    'Statement_of_Applicability': [
        ('client_name', str), ('date', str), ('standard', str),
        ('based_on_risk_assessment', str), ('controls', list),
        ('summary', dict),
    ],
    'Business_Impact_Analysis': [
        ('client_name', str), ('assessment_date', str), ('standard', str),
        ('methodology', str), ('critical_activities', list),
        ('summary', dict), ('overall_findings', str),
    ],
    'Records_of_Processing_Activities': [
        ('client_name', str), ('date', str), ('standard', str),
        ('data_controller', str), ('data_protection_officer', str),
        ('processing_activities', list), ('summary', dict),
    ],
    'Risk_Treatment_Plan': [
        ('client_name', str), ('date', str), ('standard', str),
        ('risk_assessment_reference', str), ('risks', list),
        ('summary', dict),
    ],
    'Incident_Investigation_Report': [
        ('client_name', str), ('incident_date', str), ('report_date', str),
        ('standard', str), ('incident_description', str), ('location', str),
        ('incident_type', str), ('severity', str), ('investigation_team', list),
        ('root_cause', str), ('immediate_actions', list),
        ('corrective_actions', list), ('lessons_learned', list),
        ('recommendations', list), ('status', str), ('reviewed_by', str),
    ],
    'Internal_Audit_Program': [
        ('client_name', str), ('program_year', str), ('standard', str),
        ('audit_manager', str), ('audits', list), ('summary', dict),
    ],
    'Environmental_Aspect_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('methodology', str), ('aspects', list), ('summary', dict),
    ],
    'Hazard_Identification_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('methodology', str), ('hazards', list), ('summary', dict),
    ],
    'Energy_Review': [
        ('client_name', str), ('date', str), ('standard', str),
        ('review_period', str), ('methodology', str),
        ('energy_sources', list), ('significant_uses', list),
        ('summary', dict),
    ],
    'Compliance_Obligations_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('methodology', str), ('obligations', list), ('summary', dict),
    ],
    'Service_Portfolio': [
        ('client_name', str), ('date', str), ('standard', str),
        ('portfolio_manager', str), ('services', list), ('summary', dict),
    ],
    'Service_Catalogue': [
        ('client_name', str), ('date', str), ('standard', str),
        ('catalogue_owner', str), ('catalogue_version', str),
        ('services', list), ('summary', dict),
    ],
    'Supplier_Agreement_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('register_owner', str), ('agreements', list), ('summary', dict),
    ],
    'Business_Relationship_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('relationship_manager', str), ('customers', list),
        ('summary', dict),
    ],
    'Capacity_Management_Plan': [
        ('client_name', str), ('date', str), ('standard', str),
        ('capacity_manager', str), ('review_period', str), ('scope', str),
        ('components', list), ('summary', dict),
    ],
    'Change_Management_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('change_manager', str), ('changes', list), ('summary', dict),
    ],
    'Release_Deployment_Plan': [
        ('client_name', str), ('date', str), ('standard', str),
        ('release_manager', str), ('releases', list), ('summary', dict),
    ],
    'Incident_Management_Log': [
        ('client_name', str), ('date', str), ('standard', str),
        ('incident_manager', str), ('incidents', list), ('summary', dict),
    ],
    'Problem_Management_Register': [
        ('client_name', str), ('date', str), ('standard', str),
        ('problem_manager', str), ('problems', list), ('summary', dict),
    ],
    'Service_Continuity_Plan': [
        ('client_name', str), ('date', str), ('standard', str),
        ('plan_owner', str), ('last_review_date', str),
        ('next_review_date', str), ('services', list), ('summary', dict),
    ],
    'Availability_Management_Report': [
        ('client_name', str), ('date', str), ('standard', str),
        ('report_owner', str), ('reporting_period', str),
        ('services', list), ('summary', dict),
    ],
}

SCHEDULE_FIELDS = {'day': int, 'date': str, 'time': str, 'activity': str, 'auditee': str, 'auditor': str, 'clause': str}
PARTICIPANT_FIELDS = {'name': str, 'company': str, 'department': str}

ISO_CLAUSE_PATTERN = r'\d+(?:\.\d+)*'


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
        sp = kwargs.get('system_prompt')
        if sp is not None and len(sp.strip()) < 5:
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
                for f in ('clause', 'status', 'audit_questions', 'evidence_to_check'):
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

    def _count_sentences(self, text: str) -> int:
        if not text:
            return 0
        return max(1, text.count('.') + text.count('!') + text.count('?'))

    def _check_prompt_regurgitation(self, result: dict, original_prompt: str) -> list[str]:
        errors = []
        prompt_lower = original_prompt.lower()
        for key, value in result.items():
            if isinstance(value, str) and len(value) > 100:
                value_lower = value.lower()
                overlap_words = set(value_lower.split()) & set(prompt_lower.split())
                if value_lower.split() and len(overlap_words) / len(value_lower.split()) > 0.85:
                    errors.append(f"Prompt regurgitation: '{key}' overlaps with input prompt >85%")
                    break
        return errors

    def _check_iso_clause_refs(self, result: dict) -> list[str]:
        errors = []
        if self.task_type == 'ISO_Checklist':
            sections = result.get('sections', [])
            valid_clauses = 0
            for s in sections:
                clause = s.get('clause', '')
                if clause and __import__('re').match(ISO_CLAUSE_PATTERN, clause.strip()):
                    valid_clauses += 1
            if sections and valid_clauses < len(sections) * 0.5:
                errors.append(f"ISO clause validation: only {valid_clauses}/{len(sections)} sections have valid clause numbers")
        if self.task_type in ('Audit_Plan_Stage_1', 'Audit_Plan_Stage_2'):
            schedule = result.get('daily_schedule', [])
            valid_refs = 0
            for entry in schedule:
                clause = entry.get('clause', '')
                if clause and __import__('re').search(r'\d+\.\d+', clause):
                    valid_refs += 1
            if schedule and valid_refs < len(schedule) * 0.3:
                errors.append(f"ISO clause validation: only {valid_refs}/{len(schedule)} schedule entries have clause references")
        return errors

    def score_quality(self, result: dict) -> dict:
        """Score output quality on 0-100 scale across 4 dimensions.

        Returns:
            {'overall': int, 'fields': dict, 'pass': bool}
        """
        scores = {}

        # 1) Completeness (0-40): required fields present and non-empty
        req = REQUIRED_FIELDS.get(self.task_type, [])
        present = 0
        for field, expected_type in req:
            val = result.get(field)
            if val is not None:
                if isinstance(val, str) and val.strip():
                    present += 1
                elif isinstance(val, (list, dict)) and val:
                    present += 1
                elif not isinstance(val, str):
                    present += 1
        scores['completeness'] = int((present / max(len(req), 1)) * 40)
        if present == 0:
            scores['depth'] = 0
            scores['integrity'] = 0
            scores['relevance'] = 0
            overall = 0
            threshold = MIN_SCORE_THRESHOLDS.get(self.task_type, 60)
            passed = overall >= threshold
            self._log('score_quality', {
                'overall': overall,
                'threshold': threshold,
                'pass': passed,
                'scores': scores,
            })
            return {'overall': overall, 'fields': scores, 'pass': passed}

        # 2) Content depth (0-30): sentence count, field length
        depth = 30
        min_lengths = FIELD_MIN_LENGTHS.get(self.task_type, {})
        for field, min_len in min_lengths.items():
            val = result.get(field)
            if isinstance(val, str):
                sents = self._count_sentences(val)
                if len(val.strip()) < min_len:
                    depth -= 3
                if sents < 2:
                    depth -= 2
        min_items = FIELD_MIN_ITEMS.get(self.task_type, {})
        for field, min_count in min_items.items():
            val = result.get(field)
            if isinstance(val, list) and len(val) < min_count:
                depth -= 3
        scores['depth'] = max(0, depth)

        # 3) Integrity (0-20): no placeholders, correct types
        integrity = 20
        for key, value in result.items():
            if isinstance(value, str):
                for pat in PLACEHOLDER_PATTERNS:
                    if pat.lower() in value.lower():
                        integrity -= 2
                        break
        scores['integrity'] = max(0, integrity)

        # 4) Domain relevance (0-10): ISO clause refs, audit terminology
        relevance = 10
        if self.task_type == 'ISO_Checklist':
            sections = result.get('sections', [])
            clause_hits = sum(1 for s in sections if __import__('re').match(ISO_CLAUSE_PATTERN, s.get('clause', '').strip()))
            if sections:
                relevance = int((clause_hits / len(sections)) * 10)
        elif self.task_type in ('Audit_Plan_Stage_1', 'Audit_Plan_Stage_2'):
            schedule = result.get('daily_schedule', [])
            ref_hits = sum(1 for e in schedule if __import__('re').search(r'\d+\.\d+', e.get('clause', '')))
            if schedule:
                relevance = int((ref_hits / len(schedule)) * 10)
        elif self.task_type == 'Audit_Report':
            conclusion = result.get('conclusion', '')
            has_audit_terms = any(t in str(result).lower() for t in ['nonconformity', 'finding', 'clause', 'audit', 'evidence'])
            if has_audit_terms:
                relevance = 8
            if conclusion and self._count_sentences(conclusion) >= 3:
                relevance = min(10, relevance + 2)
        scores['relevance'] = max(0, min(10, relevance))

        overall = scores['completeness'] + scores['depth'] + scores['integrity'] + scores['relevance']
        threshold = MIN_SCORE_THRESHOLDS.get(self.task_type, 60)
        passed = overall >= threshold

        self._log('score_quality', {
            'overall': overall,
            'threshold': threshold,
            'pass': passed,
            'scores': scores,
        })
        return {'overall': overall, 'fields': scores, 'pass': passed}

    def validate_quality(self, result: dict) -> list[str]:
        """Quality gate: check that output meets minimum content standards.

        Different from validate_output():
        - validate_output() checks STRUCTURE (fields present, correct types)
        - validate_quality() checks CONTENT (not too short, not generic, enough items)

        Errors here should trigger a RETRY WITH A BETTER MODEL.
        """
        errors: list[str] = []

        min_lengths = FIELD_MIN_LENGTHS.get(self.task_type, {})
        for field, min_len in min_lengths.items():
            val = result.get(field)
            if isinstance(val, str) and len(val.strip()) < min_len:
                errors.append(
                    f"Quality: '{field}' too short ({len(val.strip())} chars, "
                    f"min {min_len}). Likely generic/placeholder content."
                )

        min_items = FIELD_MIN_ITEMS.get(self.task_type, {})
        for field, min_count in min_items.items():
            val = result.get(field)
            if isinstance(val, list) and len(val) < min_count:
                errors.append(
                    f"Quality: '{field}' has {len(val)} items, "
                    f"minimum {min_count} expected for professional output."
                )

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

        if self.task_type == 'Audit_Report':
            summary = result.get('findings_summary', '')
            if summary and self._count_sentences(summary) < 4:
                errors.append(
                    "Quality: findings_summary has fewer than 4 sentences. "
                    "Must be 3-5 full paragraphs."
                )
            conclusion = result.get('conclusion', '')
            if conclusion and self._count_sentences(conclusion) < 3:
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
        """Three-phase validation with scoring and quality-aware retry.

        Phase 1: Structure (validate_output) → same-model self-heal retry
        Phase 2: Quality (validate_quality + score_quality) → flags for model upgrade
        Phase 3: Scoring → returns _score field with numeric quality score

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
                regurg_errors = self._check_prompt_regurgitation(result, prompt)
                if regurg_errors:
                    self._log('regurgitation_detected', {'errors': regurg_errors})
                    if attempt < MAX_SELF_HEAL_RETRIES:
                        current_prompt = self.build_corrective_prompt(prompt, regurg_errors)
                        continue
                    result['_quality_errors'] = regurg_errors
                    result['_audit'] = self.audit_log
                    result['_score'] = self.score_quality(result)
                    return result

                iso_errors = self._check_iso_clause_refs(result)
                if iso_errors:
                    self._log('iso_clause_validation', {'errors': iso_errors})

                quality_errors = self.validate_quality(result)
                if not quality_errors:
                    score = self.score_quality(result)
                    result['_score'] = score
                    result['_audit'] = self.audit_log
                    if not score['pass']:
                        msg = f"Score {score['overall']} below threshold {score['fields']}"
                        result['_quality_errors'] = [msg]
                        if attempt < MAX_SELF_HEAL_RETRIES:
                            current_prompt = self.build_quality_retry_prompt(prompt, [msg] + quality_errors)
                            continue
                    return result

                if attempt < MAX_SELF_HEAL_RETRIES:
                    current_prompt = self.build_quality_retry_prompt(prompt, quality_errors)
                    continue
                result['_quality_errors'] = quality_errors
                result['_audit'] = self.audit_log
                result['_score'] = self.score_quality(result)
                return result

            if attempt < MAX_SELF_HEAL_RETRIES:
                current_prompt = self.build_corrective_prompt(prompt, output_errors)
            else:
                self._log('self_heal_exhausted', {'errors': output_errors})
                result['_validation_errors'] = output_errors
                result['_audit'] = self.audit_log
                result['_score'] = self.score_quality(result)
                return result

        return {'error': 'Self-heal exhausted', '_audit': self.audit_log}
