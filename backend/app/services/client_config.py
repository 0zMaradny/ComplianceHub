"""Client configuration module — per-client settings for document generation.

Each client is fully isolated: doc code prefix, formulas, visual identity,
language mode, and active standards never mix between clients.

Client keys match the keys used in AI prompts and frontend selectors.
"""

__all__ = [
    'RiskFormulas',
    'VisualIdentity',
    'ClientConfig',
    'CLIENTS',
    'get_client',
    'get_client_by_doc_code',
    'list_clients',
    'get_doc_code',
    'validate_client_data',
]

from dataclasses import dataclass, field
from typing import Optional


# ── Formula definitions ──────────────────────────────────────────────────

@dataclass
class RiskFormulas:
    """Risk scoring formulas per client. Expressions stored as strings
    for documentation; evaluated in Excel via openpyxl formulas."""
    latent_risk: str = ""           # e.g. "S = O × Q"
    residual_risk: str = ""         # e.g. "V = S × (1 − U/4)"
    rating_method: str = ""         # e.g. "L × S" or "Nested IF"
    treatment_lookup: str = ""      # e.g. "VLOOKUP by Risk ID"


# ── Visual identity ──────────────────────────────────────────────────────

@dataclass
class VisualIdentity:
    """Color scheme and layout preferences per client."""
    primary_header: str = "#003D7A"     # TÜV blue default
    accent: str = "#C00000"             # TÜV red default
    secondary: str = "#1A3D7A"
    data_row_alt: str = "#F2F2F2"
    layout: str = "A4"
    rtl: bool = False


# ── Client definition ────────────────────────────────────────────────────

@dataclass
class ClientConfig:
    """Complete configuration for one client."""
    key: str
    name: str
    name_ar: str = ""
    doc_code_prefix: str = ""
    language: str = "en"                # "en" | "ar" | "bidi"
    standards: list = field(default_factory=list)
    formulas: RiskFormulas = field(default_factory=RiskFormulas)
    visual: VisualIdentity = field(default_factory=VisualIdentity)
    description: str = ""


# ── Active clients ───────────────────────────────────────────────────────

CLIENTS: dict[str, ClientConfig] = {
    "msd_moi": ClientConfig(
        key="msd_moi",
        name="MSD-MOI (General Directorate of Medical Services)",
        name_ar="الإدارة العامة للخدمات الطبية",
        doc_code_prefix="MSD-MOI-GRC-",
        language="ar",
        standards=["iso_22301", "iso_31000"],
        formulas=RiskFormulas(
            latent_risk="S = O × Q",
            residual_risk="V = S × (1 − U/4)",
            rating_method="VLOOKUP Treatment Plan",
            treatment_lookup="VLOOKUP by Risk ID",
        ),
        visual=VisualIdentity(
            primary_header="#004D26",
            accent="#C8A96E",
            secondary="#1A3A5C",
            data_row_alt="#E8F5E9",
            layout="A4",
            rtl=True,
        ),
        description="Arabic GRC — ISO 22301 + ISO 31000",
    ),

    "uacc": ClientConfig(
        key="uacc",
        name="UACC (Umm Alqura Cement Company — Taif Plant)",
        name_ar="شركة أسمنت أم القرى — مصنع الطائف",
        doc_code_prefix="UACC-EnMS-",
        language="en",
        standards=["iso_50001"],
        formulas=RiskFormulas(
            latent_risk="",
            residual_risk="",
            rating_method="L × S",
            treatment_lookup="Nested IF Risk Level",
        ),
        visual=VisualIdentity(
            primary_header="#003D7A",
            accent="#C00000",
            secondary="#1A3D7A",
            data_row_alt="#F2F2F2",
            layout="A4",
            rtl=False,
        ),
        description="English EnMS — ISO 50001",
    ),

    "sagco": ClientConfig(
        key="sagco",
        name="SAGCO",
        name_ar="SAGCO",
        doc_code_prefix="SAGCO-",
        language="en",
        standards=["iso_45001", "iso_14001"],
        formulas=RiskFormulas(
            latent_risk="",
            residual_risk="",
            rating_method="TBD",
            treatment_lookup="TBD",
        ),
        visual=VisualIdentity(
            primary_header="#003D7A",
            accent="#C00000",
            secondary="#1A3D7A",
            data_row_alt="#F2F2F2",
            layout="A4",
            rtl=False,
        ),
        description="ISO 45001 + ISO 14001 — Active implementation",
    ),

    "al_ahsa": ClientConfig(
        key="al_ahsa",
        name="Al-Ahsa Municipality",
        name_ar="بلدية الأحساء",
        doc_code_prefix="ALAHSA-ISMS-",
        language="ar",
        standards=["iso_27001"],
        formulas=RiskFormulas(
            latent_risk="",
            residual_risk="",
            rating_method="Likelihood × Impact Matrix",
            treatment_lookup="ISO 27001 Annex A mapping",
        ),
        visual=VisualIdentity(
            primary_header="#003D7A",
            accent="#C00000",
            secondary="#1A3D7A",
            data_row_alt="#F2F2F2",
            layout="A4",
            rtl=True,
        ),
        description="Arabic ISMS — ISO 27001",
    ),
}


# ── Lookup helpers ───────────────────────────────────────────────────────

def get_client(client_key: str) -> Optional[ClientConfig]:
    """Return client config by key, or None if not found."""
    return CLIENTS.get(client_key)


def get_client_by_doc_code(doc_code: str) -> Optional[ClientConfig]:
    """Find a client by matching its doc code prefix."""
    for client in CLIENTS.values():
        if doc_code.startswith(client.doc_code_prefix):
            return client
    return None


def list_clients() -> list[dict]:
    """Return a summary list of all active clients."""
    return [
        {
            "key": c.key,
            "name": c.name,
            "name_ar": c.name_ar,
            "doc_code_prefix": c.doc_code_prefix,
            "language": c.language,
            "standards": c.standards,
            "description": c.description,
        }
        for c in CLIENTS.values()
    ]


def get_doc_code(client_key: str, doc_type: str, sequence: int = 1) -> str:
    """Generate a document code for a client.
    
    Example: get_doc_code('msd_moi', 'RR', 1) → 'MSD-MOI-GRC-RR-001'
    """
    client = get_client(client_key)
    if not client:
        return f"UNKNOWN-{doc_type}-{sequence:03d}"
    return f"{client.doc_code_prefix}{doc_type}-{sequence:03d}"


def validate_client_data(client_key: str, data: dict) -> list[str]:
    """Validate that document data matches client expectations.
    Returns list of validation errors (empty = valid)."""
    errors = []
    client = get_client(client_key)
    if not client:
        return [f"Unknown client: {client_key}"]

    # Check doc code prefix
    doc_code = data.get("doc_code", "")
    if doc_code and not doc_code.startswith(client.doc_code_prefix):
        errors.append(
            f"Doc code '{doc_code}' does not match client prefix '{client.doc_code_prefix}'"
        )

    # Check standard compatibility
    standard = data.get("standard", "")
    if standard:
        # Map standard label to key
        standard_key = None
        for key in client.standards:
            if key.replace("_", "").lower() in standard.replace(" ", "").lower():
                standard_key = key
                break
        if standard_key is None and client.standards:
            errors.append(
                f"Standard '{standard}' not in client's active standards: {client.standards}"
            )

    return errors
