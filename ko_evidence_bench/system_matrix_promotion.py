"""Promotion gates for full-system matrix run bundles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .system_matrix_bundle import MatrixBundleResult, validate_matrix_bundle


@dataclass(frozen=True)
class PromotionGate:
    gate: str
    status: str
    evidence: str
    required: str
    blocking: bool


@dataclass(frozen=True)
class MatrixPromotionResult:
    bundle: MatrixBundleResult
    gates: tuple[PromotionGate, ...]

    @property
    def mechanical_ready(self) -> bool:
        mechanical = [
            "validation",
            "required_systems",
            "run_completeness",
            "qid_only_screen",
        ]
        return all(gate.status == "PASS" for gate in self.gates if gate.gate in mechanical)

    @property
    def promotion_ready(self) -> bool:
        return all(not gate.blocking or gate.status == "PASS" for gate in self.gates)

    @property
    def status(self) -> str:
        if self.promotion_ready:
            return "READY"
        if self.mechanical_ready:
            return "REHEARSAL_ONLY"
        return "FAIL"


def evaluate_system_matrix_promotion(
    *,
    bundle_dir: Path,
    qrels_path: Path,
    matrix_path: Path,
    min_rows: int = 500,
    k: int = 3,
) -> MatrixPromotionResult:
    bundle = validate_matrix_bundle(
        bundle_dir=bundle_dir,
        qrels_path=qrels_path,
        matrix_path=matrix_path,
        k=k,
    )
    raw_field_error_count = sum(len(system.raw_field_errors) for system in bundle.systems)
    gates = (
        PromotionGate(
            gate="validation",
            status="PASS" if bundle.validation_errors == 0 else "FAIL",
            evidence=f"{bundle.validation_errors} validation errors",
            required="0 validation errors",
            blocking=True,
        ),
        PromotionGate(
            gate="required_systems",
            status="PASS" if not bundle.missing_systems and not bundle.extra_systems else "FAIL",
            evidence=f"{len(bundle.present_systems)} present / {len(bundle.required_systems)} required",
            required="all and only matrix not-run systems are present",
            blocking=True,
        ),
        PromotionGate(
            gate="run_completeness",
            status="PASS" if bundle.complete_systems == len(bundle.required_systems) else "FAIL",
            evidence=f"{bundle.complete_systems} complete systems",
            required="every system covers every qid exactly once",
            blocking=True,
        ),
        PromotionGate(
            gate="qid_only_screen",
            status="PASS" if raw_field_error_count == 0 else "FAIL",
            evidence=f"{raw_field_error_count} raw-field errors",
            required="no raw query, answer, source, url, username, or passage fields",
            blocking=True,
        ),
        PromotionGate(
            gate="scale",
            status="PASS" if bundle.qrel_rows >= min_rows else "BLOCKED",
            evidence=f"{bundle.qrel_rows} qrel rows",
            required=f">= {min_rows} qrel rows for private full-matrix promotion",
            blocking=True,
        ),
        PromotionGate(
            gate="run_provenance",
            status="PASS" if bundle.external_systems == len(bundle.required_systems) else "BLOCKED",
            evidence=f"{bundle.external_systems} private external / {len(bundle.required_systems)} required systems",
            required="every submitted system declares private_external_run provenance",
            blocking=True,
        ),
    )
    return MatrixPromotionResult(bundle=bundle, gates=gates)
