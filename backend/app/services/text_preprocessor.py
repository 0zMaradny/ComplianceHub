"""text_preprocessor — Universal text preprocessing pipeline.

Wires into 3 entry points:
  1. preprocess_for_upload   — bytes → compressed text (documents.py)
  2. preprocess_for_generation — notes+manday → compressed prompts (ai_pipeline.py)
  3. preprocess_for_chat      — message → compressed message (ai_chat.py)

Caveman intensity levels:
  lite  — drop filler/hedging, keep full sentences
  full  — drop articles, fragments OK, short synonyms (default)
  ultra — abbreviate prose, → for causality

Arabic detection: Arabic-script text is preserved as-is.
Code blocks: guarded against compression.
"""

import re
import unicodedata

# ── Stop-word sets ─────────────────────────────────────────────────────────

FILLER = {
    'just', 'really', 'basically', 'actually', 'simply', 'quite',
    'literally', 'essentially', 'honestly', 'frankly',
    'absolutely', 'definitely', 'certainly', 'obviously',
    'surely', 'undoubtedly', 'indeed', 'moreover', 'furthermore',
    'consequently', 'additionally', 'importantly', 'ultimately',
}

HEDGING = {
    'maybe', 'perhaps', 'possibly', 'probably', 'potentially',
    'might', 'could', 'would', 'should', 'may',
    'seems', 'appears', 'tends', 'likely', 'somewhat',
}

PLEASANTRIES = {
    'sure', 'certainly', 'of course', 'happy to', 'glad to',
    "i'd be happy", "i'm happy", 'no problem', 'my pleasure',
}

ARTICLES = {'a', 'an', 'the'}

CONJUNCTIONS_WEAK = {'and', 'but', 'or', 'so', 'yet', 'for', 'nor'}

CAVEMAN_SHORT = {
    'application': 'app', 'configuration': 'config',
    'database': 'DB', 'document': 'doc',
    'authentication': 'auth', 'implementation': 'impl',
    'function': 'fn', 'parameter': 'param',
    'request': 'req', 'response': 'res',
    'management': 'mgmt', 'administration': 'admin',
    'communication': 'comm', 'development': 'dev',
    'information': 'info', 'documentation': 'docs',
    'reference': 'ref', 'previous': 'prev',
    'current': 'curr', 'temporary': 'temp',
    'additional': 'addl', 'approximately': 'approx',
    'maximum': 'max', 'minimum': 'min',
    'standard': 'std', 'specification': 'spec',
    'certification': 'cert', 'negligence': 'neg',
    'mitigation': 'mit', 'conformity': 'conf',
}

# ── Arabic range (preserve untouched) ──────────────────────────────────────
_ARABIC_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF'
                        r'\uFB50-\uFDFF\uFE70-\uFEFF]')


def _has_arabic(text: str) -> bool:
    return bool(_ARABIC_RE.search(text))


# ── Encoding normalisation ────────────────────────────────────────────────

def normalize_encoding(text: str) -> str:
    if text.startswith('\ufeff'):
        text = text[1:]
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return unicodedata.normalize('NFKC', text)


# ── Caveman compression internals ──────────────────────────────────────────

_JOIN_ARTICLES = r'\b(?:' + '|'.join(ARTICLES) + r')\b(?!\.\w)\s*'
_JOIN_FILLER = r'\b(?:' + '|'.join(re.escape(w) for w in FILLER) + r')\b'
_JOIN_HEDGING = r'\b(?:' + '|'.join(re.escape(w) for w in HEDGING) + r')\b'


def _caveman_lite(text: str) -> str:
    for p in PLEASANTRIES:
        text = re.sub(rf'\b{re.escape(p)}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(_JOIN_FILLER, '', text, flags=re.IGNORECASE)
    text = re.sub(_JOIN_HEDGING, '', text, flags=re.IGNORECASE)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def _caveman_full(text: str) -> str:
    text = _caveman_lite(text)
    text = re.sub(_JOIN_ARTICLES, '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:^|\.)\s*\b(?:and|but|or|so|yet|for|nor)\b\s*', '. ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s+\.', '.', text)
    return text.strip()


def _caveman_ultra(text: str) -> str:
    text = _caveman_full(text)
    for word, short in CAVEMAN_SHORT.items():
        text = re.sub(rf'\b{re.escape(word)}\b', short, text, flags=re.IGNORECASE)
    text = re.sub(r'\b(?:and|but|or|so|yet|for|nor)\b\s*', '', text, flags=re.IGNORECASE)
    for cause in ('because', 'therefore', 'hence', 'thus'):
        text = re.sub(rf'\b{cause}\b', '→', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s*→\s*', ' → ', text)
    return text.strip()


# ── ISO / domain compression ──────────────────────────────────────────────

def _compress_iso_codes(text: str) -> str:
    text = re.sub(r'ISO 27001:2022', 'ISO27k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 27001:2013', 'ISO27k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 9001:2015', 'ISO9k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 14001:2015', 'ISO14k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 45001:2018', 'ISO45k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 50001:2018', 'ISO50k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 22301:2019', 'ISO22k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 37301:2021', 'ISO37k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 42001:2023', 'ISO42k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 20000-1:2018', 'ISO20k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 13485:2016', 'ISO13k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 30401:2018', 'ISO30k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 27701:2025', 'ISO27p', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 31000:2018', 'ISO31k', text, flags=re.IGNORECASE)
    text = re.sub(r'ISO 10002:2018', 'ISO10k', text, flags=re.IGNORECASE)
    text = re.sub(r'clause\s+(\w[\w.]*)', r'cl.\1', text, flags=re.IGNORECASE)
    text = re.sub(r'section\s+(\w[\w.]*)', r's.\1', text, flags=re.IGNORECASE)
    text = re.sub(r'requirement\s+(\w[\w.]*)', r'req.\1', text, flags=re.IGNORECASE)
    return text


AUDIT_SHORT = {
    r'\bStatement of Applicability\b': 'SoA',
    r'\b[nN]on[- ]?[cC]onformit(?:y|ies)\b': 'NC',
    r'\bopportunit[xy].*?improvement\b': 'OFI',
    r'\bManagement Review\b': 'MgmtReview',
    r'\bCorrective Action\b': 'CA',
    r'\bPreventive Action\b': 'PA',
    r'\bRisk Assessment\b': 'RA',
    r'\bScope of Audit\b': 'Scope',
    r'\bAudit Program\b': 'Program',
    r'\bAudit Plan\b': 'Plan',
    r'\bAudit Report\b': 'Report',
    r'\bInternal Audit\b': 'IA',
}


def _compress_audit_terms(text: str) -> str:
    for pattern, replacement in AUDIT_SHORT.items():
        text = re.sub(pattern, replacement, text)
    return text


# ── Public API — entry-point functions ────────────────────────────────────

def remove_caveman_elements(text: str, intensity: str = 'full') -> str:
    """Compress text by removing filler, articles, hedging word.

    Preserves:
      - Arabic-script content (preserved as-is)
      - Fenced code blocks (`````)
      - Inline code (`…`)
    """
    if not text:
        return text
    text = normalize_encoding(text)

    lines = text.split('\n')
    out = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or _has_arabic(line):
            out.append(line)
            continue

        if intensity == 'lite':
            processed = _caveman_lite(line)
        elif intensity == 'full':
            processed = _caveman_full(line)
        elif intensity == 'ultra':
            processed = _caveman_ultra(line)
        else:
            processed = line

        out.append(processed)

    return '\n'.join(out)


def preprocess_text(text: str, intensity: str = 'full',
                     compress_iso: bool = True,
                     compress_audit: bool = True) -> dict:
    """Convenience wrapper — compress + domain shorten + stats."""
    original = text
    compressed = remove_caveman_elements(text, intensity)
    if compress_iso:
        compressed = _compress_iso_codes(compressed)
    if compress_audit:
        compressed = _compress_audit_terms(compressed)

    ol = len(original)
    pl = len(compressed)
    return {
        'text': compressed,
        'original_chars': ol,
        'processed_chars': pl,
        'savings_pct': round((1 - pl / ol) * 100, 1) if ol else 0,
    }


def preprocess_for_upload(content: bytes, filename: str,
                          compression: str = 'full') -> dict:
    """Preprocess file content at the upload entry point."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    meta = {
        'original_size': len(content),
        'format': ext,
        'text': '',
        'compression': compression,
        'savings_pct': 0,
    }

    if ext in ('txt', 'md', 'csv'):
        text = content.decode('utf-8', errors='replace')
    else:
        # DOCX / PDF / other binary — handled by file_parser downstream
        meta['format'] = ext
        return meta

    if not text.strip():
        return meta

    result = preprocess_text(text, compression)
    meta['text'] = result['text']
    meta['original_chars'] = result['original_chars']
    meta['processed_chars'] = result['processed_chars']
    meta['savings_pct'] = result['savings_pct']
    return meta


def preprocess_for_generation(notes_text: str, manday_text: str,
                               compression: str = 'full',
                               client_key: str = '') -> dict:
    """Preprocess document-generation inputs."""
    notes_result = preprocess_text(notes_text, compression) if notes_text else {}
    manday_result = preprocess_text(manday_text, compression) if manday_text else {}

    notes_compressed = notes_result.get('text', notes_text)
    manday_compressed = manday_result.get('text', manday_text)
    if client_key:
        notes_compressed = _compress_audit_terms(notes_compressed)
        manday_compressed = _compress_audit_terms(manday_compressed)

    return {
        'notes_text': notes_compressed,
        'manday_text': manday_compressed,
        'notes_savings_pct': notes_result.get('savings_pct', 0),
        'manday_savings_pct': manday_result.get('savings_pct', 0),
    }


def preprocess_for_chat(message: str, compression: str = 'full') -> dict:
    """Preprocess a chat message at the chat entry point."""
    if not message:
        return {'message': message, 'savings_pct': 0}

    if _has_arabic(message):
        return {'message': message, 'savings_pct': 0, 'arabic': True}

    result = preprocess_text(message, compression, compress_iso=False, compress_audit=False)
    return {'message': result['text'], 'savings_pct': result['savings_pct']}


def validate_and_optimize_text(text: str, max_chars: int = 32000,
                                min_chars: int = 10) -> dict:
    """Validate and optionally truncate text."""
    out = {'text': text, 'valid': True, 'warnings': []}

    if not text or len(text.strip()) < min_chars:
        out['valid'] = False
        out['warnings'].append('Text too short or empty')
        return out

    if len(text) > max_chars:
        out['text'] = text[:max_chars]
        out['truncated'] = True
        out['warnings'].append(f'Truncated {len(text)} → {max_chars} chars')

    return out


def get_compression_stats(original: str, processed: str) -> dict:
    ol = len(original)
    pl = len(processed)
    return {
        'original_chars': ol,
        'processed_chars': pl,
        'savings_pct': round((1 - pl / ol) * 100, 1) if ol else 0,
    }
