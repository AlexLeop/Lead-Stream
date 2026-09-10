from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from leadstream.entities.normalization import (
    DataValidationError,
    fingerprint_value,
    normalize_cnpj,
    normalize_domain,
    normalize_email,
    normalize_phone_br,
)

from .models import BatchItem

HEADER_ALIASES: dict[str, str] = {
    "cnpj": "cnpj",
    "documento": "cnpj",
    "razao_social": "legal_name",
    "nome_empresa": "legal_name",
    "empresa": "legal_name",
    "legal_name": "legal_name",
    "nome_fantasia": "trade_name",
    "dominio": "domain",
    "site": "domain",
    "website": "domain",
    "email": "email",
    "e_mail": "email",
    "telefone": "phone",
    "celular": "phone",
    "whatsapp": "phone",
    "phone": "phone",
}


@dataclass(frozen=True)
class HygieneResult:
    normalized: dict[str, str]
    state: str
    rules: list[str]
    issues: list[dict[str, str]]
    fingerprint: str


def normalize_header(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", (value or "").strip().casefold())
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", ascii_value).strip("_")


def canonicalize_headers(row: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for header, value in row.items():
        canonical = HEADER_ALIASES.get(normalize_header(header))
        if canonical and canonical not in result:
            result[canonical] = (value or "").strip()
    return result


def _normalize_name(value: str) -> str:
    return " ".join(value.split())


def normalize_row(row: dict[str, str]) -> HygieneResult:
    values = canonicalize_headers(row)
    normalized: dict[str, str] = {}
    rules: list[str] = []
    issues: list[dict[str, str]] = []
    normalizers = {
        "cnpj": normalize_cnpj,
        "domain": normalize_domain,
        "email": normalize_email,
        "phone": normalize_phone_br,
        "legal_name": _normalize_name,
        "trade_name": _normalize_name,
    }
    for field, normalizer in normalizers.items():
        original = values.get(field, "")
        if not original:
            continue
        try:
            result = normalizer(original)
        except DataValidationError as exc:
            issues.append({"field": field, "code": "INVALID", "message": str(exc)})
            continue
        if not result:
            issues.append({"field": field, "code": "EMPTY", "message": "Valor vazio."})
            continue
        normalized[field] = result
        if result != original:
            rules.append(f"NORMALIZE_{field.upper()}")
    identity = next(
        (
            (field, normalized[field])
            for field in ("cnpj", "email", "phone", "domain", "legal_name")
            if normalized.get(field)
        ),
        None,
    )
    if identity is None:
        issues.append(
            {
                "field": "registro",
                "code": "MISSING_IDENTIFIER",
                "message": "Nenhum identificador utilizável foi encontrado.",
            }
        )
        fingerprint = ""
    else:
        fingerprint = fingerprint_value(identity)
    if issues:
        state = BatchItem.HygieneState.INVALID
    elif rules:
        state = BatchItem.HygieneState.CORRECTED
    else:
        state = BatchItem.HygieneState.UNCHANGED
    return HygieneResult(
        normalized=normalized,
        state=state,
        rules=rules,
        issues=issues,
        fingerprint=fingerprint,
    )


def original_json(row: dict[str, Any]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value) for key, value in row.items()}
