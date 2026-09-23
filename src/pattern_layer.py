"""HYDRANGEA Tier 3 schemas and injectable local embedding boundary.

This module deliberately does not choose similarity thresholds, merge memories,
or detect contradictions. It establishes the persistent, auditable structures
needed to calibrate those behaviors without rewriting source memories.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping, Protocol, Sequence, runtime_checkable

from logic.compression_engine import CompressionResult
from src.memory_compression_prototype import Tier2ParseResult


MINILM_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PatternStatus = Literal["candidate", "pattern"]
SimilarityMetric = Literal["cosine"]
ContradictionDetection = Literal["schema_only"]


class PatternSchemaError(ValueError):
    """Raised when a persisted Tier 3 object violates an invariant."""


class EmbeddingDependencyUnavailableError(RuntimeError):
    """Raised when the optional local embedding dependency is unavailable."""


@dataclass(frozen=True)
class PatternPolicy:
    """Versioned policy snapshot used to create and compare pattern nodes.

    Thresholds remain ``None`` until a larger labeled calibration set has been
    reviewed. Auto-merge cannot be enabled while they are unset.
    """

    policy_id: str
    embedding_model: str
    embedding_revision: str
    promotion_threshold: int = 3
    similarity_metric: SimilarityMetric = "cosine"
    merge_threshold: float | None = None
    ambiguity_threshold: float | None = None
    auto_merge_enabled: bool = False
    contradiction_detection: ContradictionDetection = "schema_only"
    schema_version: str = "hydrangea.pattern-policy.v1"

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise PatternSchemaError("policy_id must be a durable non-empty identifier")
        if not self.embedding_model.strip() or not self.embedding_revision.strip():
            raise PatternSchemaError("embedding model and revision must be recorded")
        if self.promotion_threshold < 2:
            raise PatternSchemaError("promotion_threshold must require recurrence")
        if self.similarity_metric != "cosine":
            raise PatternSchemaError("only cosine similarity is supported")
        if self.contradiction_detection != "schema_only":
            raise PatternSchemaError(
                "contradiction detection is schema-only in this release"
            )
        thresholds = (self.merge_threshold, self.ambiguity_threshold)
        if (thresholds[0] is None) != (thresholds[1] is None):
            raise PatternSchemaError("merge and ambiguity thresholds must be set together")
        if self.merge_threshold is not None and self.ambiguity_threshold is not None:
            if not 0 <= self.ambiguity_threshold < self.merge_threshold <= 1:
                raise PatternSchemaError(
                    "thresholds must satisfy 0 <= ambiguity < merge <= 1"
                )
        if self.auto_merge_enabled and self.merge_threshold is None:
            raise PatternSchemaError("auto-merge requires calibrated thresholds")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "embedding_model": self.embedding_model,
            "embedding_revision": self.embedding_revision,
            "promotion_threshold": self.promotion_threshold,
            "similarity_metric": self.similarity_metric,
            "merge_threshold": self.merge_threshold,
            "ambiguity_threshold": self.ambiguity_threshold,
            "auto_merge_enabled": self.auto_merge_enabled,
            "contradiction_detection": self.contradiction_detection,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> PatternPolicy:
        merge = payload.get("merge_threshold")
        ambiguity = payload.get("ambiguity_threshold")
        return cls(
            policy_id=str(payload["policy_id"]),
            embedding_model=str(payload["embedding_model"]),
            embedding_revision=str(payload["embedding_revision"]),
            promotion_threshold=int(payload["promotion_threshold"]),
            similarity_metric=str(payload["similarity_metric"]),  # type: ignore[arg-type]
            merge_threshold=float(merge) if merge is not None else None,
            ambiguity_threshold=float(ambiguity) if ambiguity is not None else None,
            auto_merge_enabled=bool(payload["auto_merge_enabled"]),
            contradiction_detection=str(payload["contradiction_detection"]),  # type: ignore[arg-type]
            schema_version=str(payload.get("schema_version", "hydrangea.pattern-policy.v1")),
        )


@dataclass(frozen=True)
class PatternMemory:
    """Immutable Tier 3 input retaining durable source evidence."""

    source_id: str
    observed_at: str
    original_text: str
    anchors: tuple[str, ...]
    system_codes: tuple[str, ...]
    tier1_schema_version: str
    tier2_schema_version: str | None = None
    schema_version: str = "hydrangea.pattern-memory.v1"

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise PatternSchemaError("source_id must be a durable non-empty identifier")
        if not self.observed_at.strip():
            raise PatternSchemaError("observed_at must be recorded")
        if not self.original_text.strip():
            raise PatternSchemaError("original_text cannot be empty")
        if not self.tier1_schema_version.strip():
            raise PatternSchemaError("tier1_schema_version must be recorded")
        object.__setattr__(self, "anchors", tuple(self.anchors))
        object.__setattr__(self, "system_codes", tuple(self.system_codes))

    @classmethod
    def from_results(
        cls,
        *,
        source_id: str,
        observed_at: str,
        tier1: CompressionResult,
        tier2: Tier2ParseResult | None = None,
    ) -> PatternMemory:
        system_codes = ()
        tier2_schema_version = None
        if tier2 is not None:
            if tier2.tier1.get("original") != tier1.original:
                raise PatternSchemaError("Tier 1 and Tier 2 originals do not match")
            system_codes = tuple(entry.code for entry in tier2.system_codes)
            tier2_schema_version = tier2.schema_version
        return cls(
            source_id=source_id,
            observed_at=observed_at,
            original_text=tier1.original,
            anchors=tuple(tier1.anchors),
            system_codes=system_codes,
            tier1_schema_version=tier1.schema_version,
            tier2_schema_version=tier2_schema_version,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source_id": self.source_id,
            "observed_at": self.observed_at,
            "original_text": self.original_text,
            "anchors": list(self.anchors),
            "system_codes": list(self.system_codes),
            "tier1_schema_version": self.tier1_schema_version,
            "tier2_schema_version": self.tier2_schema_version,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> PatternMemory:
        return cls(
            source_id=str(payload["source_id"]),
            observed_at=str(payload["observed_at"]),
            original_text=str(payload["original_text"]),
            anchors=tuple(str(value) for value in payload.get("anchors", [])),  # type: ignore[arg-type]
            system_codes=tuple(str(value) for value in payload.get("system_codes", [])),  # type: ignore[arg-type]
            tier1_schema_version=str(payload["tier1_schema_version"]),
            tier2_schema_version=(
                str(payload["tier2_schema_version"])
                if payload.get("tier2_schema_version") is not None
                else None
            ),
            schema_version=str(payload.get("schema_version", "hydrangea.pattern-memory.v1")),
        )


@dataclass(frozen=True)
class PatternRelation:
    """An ambiguity or confirmed-contradiction link to retained evidence."""

    source_id: str
    similarity_score: float
    reason: str
    recorded_at: str
    evidence_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.similarity_score <= 1:
            raise PatternSchemaError("similarity_score must be between 0 and 1")
        if not self.source_id.strip() or not self.reason.strip() or not self.recorded_at.strip():
            raise PatternSchemaError("relation source, reason, and timestamp are required")
        object.__setattr__(self, "evidence_codes", tuple(self.evidence_codes))

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "similarity_score": self.similarity_score,
            "reason": self.reason,
            "recorded_at": self.recorded_at,
            "evidence_codes": list(self.evidence_codes),
        }


@dataclass(frozen=True)
class PatternHistoryEntry:
    """One append-only interpretation or re-weighting event."""

    event_id: str
    recorded_at: str
    action: str
    reason: str
    details: Mapping[str, str]

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.event_id, self.recorded_at, self.action, self.reason)):
            raise PatternSchemaError("history event fields must be non-empty")
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "recorded_at": self.recorded_at,
            "action": self.action,
            "reason": self.reason,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class PatternNode:
    """Persistent candidate or promoted pattern; source links are never pruned."""

    pattern_id: str
    policy_id: str
    status: PatternStatus
    instance_links: tuple[str, ...]
    representative_source_id: str
    representative_text: str
    anchors: Mapping[str, int]
    recurrence_count: int
    first_seen: str
    last_seen: str
    cohesion_score: float | None
    ambiguity_links: tuple[PatternRelation, ...]
    contradiction_links: tuple[PatternRelation, ...]
    history: tuple[PatternHistoryEntry, ...]
    embedding_model: str
    embedding_revision: str
    embedding_dimensions: int
    centroid: tuple[float, ...]
    promotion_threshold_snapshot: int = 3
    schema_version: str = "hydrangea.pattern-node.v1"

    def __post_init__(self) -> None:
        if not self.pattern_id.strip() or not self.policy_id.strip():
            raise PatternSchemaError("pattern_id and policy_id must be durable identifiers")
        if self.status not in {"candidate", "pattern"}:
            raise PatternSchemaError("status must be 'candidate' or 'pattern'")
        object.__setattr__(self, "instance_links", tuple(self.instance_links))
        object.__setattr__(self, "ambiguity_links", tuple(self.ambiguity_links))
        object.__setattr__(self, "contradiction_links", tuple(self.contradiction_links))
        object.__setattr__(self, "history", tuple(self.history))
        object.__setattr__(self, "centroid", tuple(self.centroid))
        if not self.instance_links or len(set(self.instance_links)) != len(self.instance_links):
            raise PatternSchemaError("instance_links must be non-empty and unique")
        if self.representative_source_id not in self.instance_links:
            raise PatternSchemaError("representative source must be a linked instance")
        if not self.representative_text.strip():
            raise PatternSchemaError("representative_text must be a verbatim source instance")
        if not self.first_seen.strip() or not self.last_seen.strip():
            raise PatternSchemaError("first_seen and last_seen must be recorded")
        if not self.embedding_model.strip() or not self.embedding_revision.strip():
            raise PatternSchemaError("embedding model and revision must be recorded")
        if self.recurrence_count != len(self.instance_links):
            raise PatternSchemaError("recurrence_count must equal the linked-instance count")
        if self.status == "pattern" and self.recurrence_count < self.promotion_threshold_snapshot:
            raise PatternSchemaError("a promoted pattern has not met its recurrence threshold")
        if self.promotion_threshold_snapshot < 2:
            raise PatternSchemaError("promotion threshold snapshot must require recurrence")
        if self.cohesion_score is not None and not 0 <= self.cohesion_score <= 1:
            raise PatternSchemaError("cohesion_score must be between 0 and 1")
        if self.embedding_dimensions <= 0 or len(self.centroid) != self.embedding_dimensions:
            raise PatternSchemaError("centroid must match the recorded embedding dimensions")
        if not all(math.isfinite(value) for value in self.centroid):
            raise PatternSchemaError("centroid values must be finite")
        anchor_copy = dict(self.anchors)
        if any(not anchor or count <= 0 for anchor, count in anchor_copy.items()):
            raise PatternSchemaError("anchor counts must use non-empty keys and positive values")
        object.__setattr__(self, "anchors", MappingProxyType(anchor_copy))

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "pattern_id": self.pattern_id,
            "policy_id": self.policy_id,
            "status": self.status,
            "instance_links": list(self.instance_links),
            "representative_source_id": self.representative_source_id,
            "representative_text": self.representative_text,
            "anchors": dict(self.anchors),
            "recurrence_count": self.recurrence_count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "cohesion_score": self.cohesion_score,
            "ambiguity_links": [link.to_dict() for link in self.ambiguity_links],
            "contradiction_links": [link.to_dict() for link in self.contradiction_links],
            "history": [entry.to_dict() for entry in self.history],
            "embedding_model": self.embedding_model,
            "embedding_revision": self.embedding_revision,
            "embedding_dimensions": self.embedding_dimensions,
            "centroid": list(self.centroid),
            "promotion_threshold_snapshot": self.promotion_threshold_snapshot,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> PatternNode:
        def relation_from_dict(value: Mapping[str, object]) -> PatternRelation:
            return PatternRelation(
                source_id=str(value["source_id"]),
                similarity_score=float(value["similarity_score"]),
                reason=str(value["reason"]),
                recorded_at=str(value["recorded_at"]),
                evidence_codes=tuple(str(code) for code in value.get("evidence_codes", [])),  # type: ignore[arg-type]
            )

        def history_from_dict(value: Mapping[str, object]) -> PatternHistoryEntry:
            return PatternHistoryEntry(
                event_id=str(value["event_id"]),
                recorded_at=str(value["recorded_at"]),
                action=str(value["action"]),
                reason=str(value["reason"]),
                details=value.get("details", {}),  # type: ignore[arg-type]
            )

        return cls(
            pattern_id=str(payload["pattern_id"]),
            policy_id=str(payload["policy_id"]),
            status=str(payload["status"]),  # type: ignore[arg-type]
            instance_links=tuple(str(value) for value in payload["instance_links"]),  # type: ignore[arg-type]
            representative_source_id=str(payload["representative_source_id"]),
            representative_text=str(payload["representative_text"]),
            anchors=payload.get("anchors", {}),  # type: ignore[arg-type]
            recurrence_count=int(payload["recurrence_count"]),
            first_seen=str(payload["first_seen"]),
            last_seen=str(payload["last_seen"]),
            cohesion_score=(
                float(payload["cohesion_score"])
                if payload.get("cohesion_score") is not None
                else None
            ),
            ambiguity_links=tuple(
                relation_from_dict(value) for value in payload.get("ambiguity_links", [])  # type: ignore[arg-type]
            ),
            contradiction_links=tuple(
                relation_from_dict(value) for value in payload.get("contradiction_links", [])  # type: ignore[arg-type]
            ),
            history=tuple(
                history_from_dict(value) for value in payload.get("history", [])  # type: ignore[arg-type]
            ),
            embedding_model=str(payload["embedding_model"]),
            embedding_revision=str(payload["embedding_revision"]),
            embedding_dimensions=int(payload["embedding_dimensions"]),
            centroid=tuple(float(value) for value in payload["centroid"]),  # type: ignore[arg-type]
            promotion_threshold_snapshot=int(payload.get("promotion_threshold_snapshot", 3)),
            schema_version=str(payload.get("schema_version", "hydrangea.pattern-node.v1")),
        )


@dataclass(frozen=True)
class EmbeddedMemory:
    """An embedding tied to exact source text and a pinned local model."""

    source_id: str
    source_text_sha256: str
    embedding_model: str
    embedding_revision: str
    vector: tuple[float, ...]

    def __post_init__(self) -> None:
        vector = tuple(float(value) for value in self.vector)
        is_sha256 = len(self.source_text_sha256) == 64 and all(
            character in "0123456789abcdef" for character in self.source_text_sha256
        )
        if not self.source_id.strip() or not is_sha256:
            raise PatternSchemaError("embedded memory requires a source ID and SHA-256 digest")
        if not self.embedding_model.strip() or not self.embedding_revision.strip():
            raise PatternSchemaError("embedded memory must record model and revision")
        if not vector or not all(math.isfinite(value) for value in vector):
            raise PatternSchemaError("embedding vector must be non-empty and finite")
        object.__setattr__(self, "vector", vector)

    @property
    def dimensions(self) -> int:
        return len(self.vector)

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "source_text_sha256": self.source_text_sha256,
            "embedding_model": self.embedding_model,
            "embedding_revision": self.embedding_revision,
            "vector": list(self.vector),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> EmbeddedMemory:
        return cls(
            source_id=str(payload["source_id"]),
            source_text_sha256=str(payload["source_text_sha256"]),
            embedding_model=str(payload["embedding_model"]),
            embedding_revision=str(payload["embedding_revision"]),
            vector=tuple(float(value) for value in payload["vector"]),  # type: ignore[arg-type]
        )


@runtime_checkable
class Embedder(Protocol):
    """Injectable embedding interface used by calibration and later matching."""

    model_name: str
    model_revision: str

    @property
    def dimensions(self) -> int | None: ...

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...


class PatternEncoder:
    """Creates auditable embeddings from original text, never compressed gists."""

    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    def encode(self, memory: PatternMemory) -> EmbeddedMemory:
        vectors = self.embedder.embed([memory.original_text])
        if len(vectors) != 1:
            raise PatternSchemaError("embedder must return one vector per input text")
        vector = tuple(float(value) for value in vectors[0])
        if not vector or not all(math.isfinite(value) for value in vector):
            raise PatternSchemaError("embedding vector must be non-empty and finite")
        dimensions = self.embedder.dimensions
        if dimensions is not None and len(vector) != dimensions:
            raise PatternSchemaError("embedding vector does not match declared dimensions")
        digest = hashlib.sha256(memory.original_text.encode("utf-8")).hexdigest()
        return EmbeddedMemory(
            source_id=memory.source_id,
            source_text_sha256=digest,
            embedding_model=self.embedder.model_name,
            embedding_revision=self.embedder.model_revision,
            vector=vector,
        )


class SentenceTransformerEmbedder:
    """Optional CPU-local MiniLM adapter; no API embedding service is used."""

    def __init__(
        self,
        *,
        revision: str,
        model_name: str = MINILM_MODEL_NAME,
        device: str = "cpu",
        local_files_only: bool = False,
    ):
        if not revision.strip():
            raise PatternSchemaError("a pinned model revision is required")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise EmbeddingDependencyUnavailableError(
                "Tier 3 embeddings require: pip install -e '.[tier3]'"
            ) from exc

        self.model_name = model_name
        self.model_revision = revision
        self._model = SentenceTransformer(
            model_name,
            revision=revision,
            device=device,
            local_files_only=local_files_only,
        )
        self._dimensions = self._model.get_sentence_embedding_dimension()

    @property
    def dimensions(self) -> int | None:
        return self._dimensions

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        vectors = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()
