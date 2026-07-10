"""Validate qid-only run bundles for the full system matrix."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .metrics import load_jsonl, score_run
from .schemas import validate_qrel, validate_run
from .surface import score_surface_run
from .system_matrix import load_matrix, system_rows


ALLOWED_RUN_KEYS = {"qid", "route_pred", "abstained", "ranked"}
ALLOWED_RANKED_KEYS = {"evidence_id", "source_tier", "score"}
PROVENANCE_KINDS = {"synthetic_fixture", "private_external_run"}
ALLOWED_PROVENANCE_KEYS = {
    "kind",
    "generator",
    "runner_commit",
    "corpus_fingerprint",
    "qrels_fingerprint",
    "engine",
    "model_id",
    "model_revision",
    "generated_at",
}


@dataclass(frozen=True)
class BundleSystemResult:
    system_id: str
    family: str
    stage: str
    run_kind: str
    rows: int
    missing_qids: tuple[str, ...]
    extra_qids: tuple[str, ...]
    duplicate_qids: tuple[str, ...]
    schema_errors: tuple[str, ...]
    raw_field_errors: tuple[str, ...]
    route_accuracy: float
    evidence_sufficiency: float
    wrong_source_rate: float
    clause_recall: float
    task_success: float
    worst_surface: float
    avg_intent_spread: float

    @property
    def complete(self) -> bool:
        return not (
            self.missing_qids
            or self.extra_qids
            or self.duplicate_qids
            or self.schema_errors
            or self.raw_field_errors
        )


@dataclass(frozen=True)
class MatrixBundleResult:
    label_status: str
    qrel_rows: int
    required_systems: tuple[str, ...]
    present_systems: tuple[str, ...]
    missing_systems: tuple[str, ...]
    extra_systems: tuple[str, ...]
    systems: tuple[BundleSystemResult, ...]

    @property
    def complete_systems(self) -> int:
        return sum(1 for system in self.systems if system.complete)

    @property
    def fixture_systems(self) -> int:
        return sum(1 for system in self.systems if system.run_kind == "synthetic_fixture")

    @property
    def external_systems(self) -> int:
        return sum(1 for system in self.systems if system.run_kind == "private_external_run")

    @property
    def validation_errors(self) -> int:
        return (
            len(self.missing_systems)
            + len(self.extra_systems)
            + sum(
                len(system.missing_qids)
                + len(system.extra_qids)
                + len(system.duplicate_qids)
                + len(system.schema_errors)
                + len(system.raw_field_errors)
                for system in self.systems
            )
        )


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def runnable_required_system_ids(matrix_path: Path) -> list[str]:
    matrix = load_matrix(matrix_path)
    return [
        str(row["system_id"])
        for row in system_rows(matrix)
        if row.get("current_status") == "not_run" and row.get("claim_scope") == "missing_for_full_matrix"
    ]


def matrix_row_by_id(matrix_path: Path) -> dict[str, dict[str, Any]]:
    matrix = load_matrix(matrix_path)
    return {str(row["system_id"]): row for row in system_rows(matrix)}


def duplicate_values(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return tuple(sorted(duplicates))


def validate_qrels(qrels: list[dict[str, Any]]) -> None:
    for qrel in qrels:
        validate_qrel(qrel)


def raw_field_errors(row: dict[str, Any], *, row_index: int) -> list[str]:
    errors: list[str] = []
    extra = sorted(set(row) - ALLOWED_RUN_KEYS)
    if extra:
        errors.append(f"row {row_index} has non-qid-only top-level fields: {extra}")
    ranked = row.get("ranked", [])
    if isinstance(ranked, list):
        for ranked_index, item in enumerate(ranked):
            if not isinstance(item, dict):
                continue
            extra_ranked = sorted(set(item) - ALLOWED_RANKED_KEYS)
            if extra_ranked:
                errors.append(
                    f"row {row_index} ranked {ranked_index} has non-qid-only fields: {extra_ranked}"
                )
    return errors


def resolved_provenance(system: dict[str, Any], bundle_provenance: Any) -> tuple[dict[str, Any], list[str]]:
    """Merge bundle defaults with a system's model-specific provenance."""

    errors: list[str] = []
    provenance: dict[str, Any] = {}
    if bundle_provenance is not None:
        if not isinstance(bundle_provenance, dict):
            errors.append("bundle provenance must be an object")
        else:
            provenance.update(bundle_provenance)
    system_provenance = system.get("provenance")
    if system_provenance is not None:
        if not isinstance(system_provenance, dict):
            errors.append("system provenance must be an object")
        else:
            provenance.update(system_provenance)
    return provenance, errors


def provenance_errors(provenance: dict[str, Any], *, qrels_sha256: str) -> tuple[str, list[str]]:
    """Validate enough provenance to distinguish a fixture from an external run."""

    errors: list[str] = []
    extra = sorted(set(provenance) - ALLOWED_PROVENANCE_KEYS)
    if extra:
        errors.append(f"provenance has unsupported fields: {extra}")

    run_kind = str(provenance.get("kind") or "unspecified")
    if run_kind not in PROVENANCE_KINDS:
        errors.append(f"provenance kind must be one of {sorted(PROVENANCE_KINDS)}")
        return run_kind, errors

    required = {"kind", "corpus_fingerprint", "qrels_fingerprint", "generated_at"}
    if run_kind == "synthetic_fixture":
        required.add("generator")
    else:
        required.update({"runner_commit", "engine", "model_id", "model_revision"})
    for key in sorted(required):
        value = provenance.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"provenance {key} must be a non-empty string")

    expected_qrels_fingerprint = f"sha256:{qrels_sha256}"
    if provenance.get("qrels_fingerprint") != expected_qrels_fingerprint:
        errors.append("provenance qrels_fingerprint does not match the supplied qrels")
    return run_kind, errors


def validate_system_run(
    *,
    system: dict[str, Any],
    bundle_dir: Path,
    qrels: list[dict[str, Any]],
    matrix_rows: dict[str, dict[str, Any]],
    bundle_provenance: Any,
    qrels_sha256: str,
    k: int,
) -> BundleSystemResult:
    system_id = str(system.get("system_id") or "")
    run_path = bundle_dir / str(system.get("run") or "")
    matrix_row = matrix_rows.get(system_id, {})
    family = str(system.get("family") or matrix_row.get("family") or "")
    stage = str(system.get("stage") or matrix_row.get("stage") or "")
    schema_errors: list[str] = []
    raw_errors: list[str] = []
    provenance, provenance_validation_errors = resolved_provenance(system, bundle_provenance)
    run_kind, provenance_field_errors = provenance_errors(provenance, qrels_sha256=qrels_sha256)
    schema_errors.extend(provenance_validation_errors)
    schema_errors.extend(provenance_field_errors)

    if not system_id:
        schema_errors.append("system_id is required")
    if not run_path.exists():
        schema_errors.append(f"run file does not exist: {run_path}")
        run_rows: list[dict[str, Any]] = []
    else:
        run_rows = load_jsonl(run_path)

    if matrix_row:
        if family != matrix_row.get("family"):
            schema_errors.append(f"family mismatch: {family} != {matrix_row.get('family')}")
        if stage != matrix_row.get("stage"):
            schema_errors.append(f"stage mismatch: {stage} != {matrix_row.get('stage')}")
    else:
        schema_errors.append("system_id is not present in docs/system_matrix.json")

    qrel_qids = sorted(str(row["qid"]) for row in qrels)
    run_qids = [str(row.get("qid") or "") for row in run_rows]
    for idx, row in enumerate(run_rows, 1):
        try:
            validate_run(row)
        except ValueError as exc:
            schema_errors.append(f"row {idx}: {exc}")
        raw_errors.extend(raw_field_errors(row, row_index=idx))

    missing_qids = tuple(sorted(set(qrel_qids) - set(run_qids)))
    extra_qids = tuple(sorted(set(run_qids) - set(qrel_qids)))
    duplicates = duplicate_values(run_qids)

    if schema_errors or raw_errors:
        route_accuracy = evidence_sufficiency = wrong_source_rate = clause_recall = 0.0
        task_success = worst_surface = avg_intent_spread = 0.0
    else:
        score = score_run(qrels, run_rows, k=k)
        surface = score_surface_run(qrels, run_rows, k=k)
        route_accuracy = score["route_accuracy"]
        evidence_sufficiency = score[f"evidence_sufficiency@{k}"]
        wrong_source_rate = score[f"wrong_source_rate@{k}"]
        clause_recall = score[f"clause_recall@{k}"]
        task_success = surface[f"task_success@{k}"]
        worst_surface = surface[f"worst_surface_task_success@{k}"]
        avg_intent_spread = surface["avg_intent_surface_spread"]

    return BundleSystemResult(
        system_id=system_id,
        family=family,
        stage=stage,
        run_kind=run_kind,
        rows=len(run_rows),
        missing_qids=missing_qids,
        extra_qids=extra_qids,
        duplicate_qids=duplicates,
        schema_errors=tuple(schema_errors),
        raw_field_errors=tuple(raw_errors),
        route_accuracy=route_accuracy,
        evidence_sufficiency=evidence_sufficiency,
        wrong_source_rate=wrong_source_rate,
        clause_recall=clause_recall,
        task_success=task_success,
        worst_surface=worst_surface,
        avg_intent_spread=avg_intent_spread,
    )


def validate_matrix_bundle(
    *,
    bundle_dir: Path,
    qrels_path: Path,
    matrix_path: Path,
    k: int = 3,
) -> MatrixBundleResult:
    manifest = load_json(bundle_dir / "manifest.json")
    qrels = load_jsonl(qrels_path)
    validate_qrels(qrels)
    qrels_sha256 = sha256_file(qrels_path)
    required = tuple(runnable_required_system_ids(matrix_path))
    matrix_rows = matrix_row_by_id(matrix_path)
    systems = manifest.get("systems")
    if not isinstance(systems, list):
        raise ValueError("bundle manifest must contain a systems list")

    present = tuple(str(system.get("system_id") or "") for system in systems)
    missing = tuple(sorted(set(required) - set(present)))
    extra = tuple(sorted(set(present) - set(required)))
    system_results = tuple(
        validate_system_run(
            system=system,
            bundle_dir=bundle_dir,
            qrels=qrels,
            matrix_rows=matrix_rows,
            bundle_provenance=manifest.get("provenance"),
            qrels_sha256=qrels_sha256,
            k=k,
        )
        for system in systems
    )
    return MatrixBundleResult(
        label_status=str(manifest.get("label_status") or "unspecified"),
        qrel_rows=len(qrels),
        required_systems=required,
        present_systems=present,
        missing_systems=missing,
        extra_systems=extra,
        systems=system_results,
    )
