from fastapi import APIRouter, HTTPException

from app.routes import compliance_frameworks

router = APIRouter(tags=["Compliance"])

from app.services.clause_data import get_clause_data, get_annex_a_data


@router.get("/api/compliance/frameworks")
def get_frameworks():
    return {'frameworks': compliance_frameworks}


@router.get("/api/compliance/checklist/{framework_id}")
def get_checklist(framework_id: str):
    framework = compliance_frameworks.get(framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail='Framework not found')

    return {
        'framework': framework,
        'checklist_items': [
            {
                'pillar': p['id'],
                'pillar_label': p['label'],
                'items': [
                    f'Document {p["label"]} policy',
                    f'Assign responsibility for {p["label"]}',
                    f'Establish procedures for {p["label"]}',
                ],
            }
            for p in framework['pillars']
        ],
    }


@router.get("/api/compliance/standards/{standard_id}/clauses")
def get_standard_clauses(standard_id: str):
    try:
        raw = get_clause_data(standard_id)
        annex = get_annex_a_data(standard_id)
        items = []
        seen = set()

        if isinstance(raw, dict) and isinstance(raw.get('sections'), dict):
            for sid, section in raw['sections'].items():
                items.append({
                    'id': sid,
                    'title': section.get('title', ''),
                    'description': section.get('evidence', ''),
                    'sub_items': list(section.get('sub_sections', {}).values()) if isinstance(section.get('sub_sections'), dict) else [],
                })
        else:
            for key, c in (raw if isinstance(raw, dict) else {}).items():
                num = c.get('clause', c.get('id', key))
                if num in seen:
                    continue
                seen.add(num)
                items.append({
                    'id': num,
                    'title': c.get('title', ''),
                    'description': c.get('description', c.get('text', '')),
                })

        return {
            'standard_id': standard_id,
            'clauses': items,
            'annex_a': annex or {},
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Standard not found: {str(e)}')


@router.get("/api/compliance/assessment/{standard_key}")
def get_compliance_assessment(standard_key: str):
    from app.services.db import load_compliance_assessment
    data = load_compliance_assessment(standard_key)
    return {'standard_key': standard_key, 'assessments': data or {}}


@router.put("/api/compliance/assessment/{standard_key}")
def save_compliance_assessment(standard_key: str, data: dict):
    from app.services.db import save_compliance_assessment
    assessments = data.get('assessments', {})
    save_compliance_assessment(standard_key, assessments)
    return {'status': 'ok', 'standard_key': standard_key}
