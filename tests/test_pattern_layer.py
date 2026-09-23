import hashlib
import json
import math
import types
import unittest
from unittest import mock

from logic.compression_engine import compress_with_metadata
from src.memory_compression_prototype import SystemCodeEntry, Tier2ParseResult
from src.pattern_layer import (
    MINILM_MODEL_NAME,
    PatternEncoder,
    EmbeddedMemory,
    PatternHistoryEntry,
    PatternMemory,
    PatternNode,
    PatternPolicy,
    PatternRelation,
    PatternSchemaError,
    SentenceTransformerEmbedder,
)


class FakeEmbedder:
    model_name = MINILM_MODEL_NAME
    model_revision = "test-revision"
    dimensions = 3

    def __init__(self, vectors=None):
        self.vectors = [[0.2, 0.4, 0.8]] if vectors is None else vectors
        self.inputs = []

    def embed(self, texts):
        self.inputs.append(list(texts))
        return self.vectors


class PatternLayerTests(unittest.TestCase):
    def make_memory(self):
        return PatternMemory(
            source_id="memory-001",
            observed_at="2026-09-22T10:00:00-07:00",
            original_text="Nova smiled as the echo returned.",
            anchors=("smiled", "echo"),
            system_codes=("[SUB:NOVA][ACT:SMILE]",),
            tier1_schema_version="hydrangea.tier1.v2",
            tier2_schema_version="hydrangea.tier2.v1",
        )

    def make_node(self, **overrides):
        values = {
            "pattern_id": "pattern-001",
            "policy_id": "policy-minilm-calibration-1",
            "status": "candidate",
            "instance_links": ("memory-001",),
            "representative_source_id": "memory-001",
            "representative_text": "Nova smiled as the echo returned.",
            "anchors": {"smiled": 1, "echo": 1},
            "recurrence_count": 1,
            "first_seen": "2026-09-22T10:00:00-07:00",
            "last_seen": "2026-09-22T10:00:00-07:00",
            "cohesion_score": None,
            "ambiguity_links": (),
            "contradiction_links": (),
            "history": (),
            "embedding_model": MINILM_MODEL_NAME,
            "embedding_revision": "test-revision",
            "embedding_dimensions": 3,
            "centroid": (0.2, 0.4, 0.8),
        }
        values.update(overrides)
        return PatternNode(**values)

    def test_policy_records_approved_defaults_without_enabling_merges(self):
        policy = PatternPolicy(
            policy_id="policy-minilm-calibration-1",
            embedding_model=MINILM_MODEL_NAME,
            embedding_revision="test-revision",
        )

        self.assertEqual(policy.promotion_threshold, 3)
        self.assertIsNone(policy.merge_threshold)
        self.assertIsNone(policy.ambiguity_threshold)
        self.assertFalse(policy.auto_merge_enabled)
        self.assertEqual(policy.contradiction_detection, "schema_only")
        self.assertEqual(PatternPolicy.from_dict(policy.to_dict()), policy)

        with self.assertRaises(PatternSchemaError):
            PatternPolicy(
                policy_id="bad",
                embedding_model=MINILM_MODEL_NAME,
                embedding_revision="test-revision",
                merge_threshold=0.9,
            )
        with self.assertRaises(PatternSchemaError):
            PatternPolicy(
                policy_id="bad",
                embedding_model=MINILM_MODEL_NAME,
                embedding_revision="test-revision",
                auto_merge_enabled=True,
            )

    def test_tier_handoff_retains_original_and_secondary_system_codes(self):
        tier1 = compress_with_metadata(
            "Nova smiled as the echo returned.", "expressive"
        )
        tier2 = Tier2ParseResult(
            schema_version="hydrangea.tier2.v1",
            tier1=tier1.to_dict(),
            system_codes=[
                SystemCodeEntry(
                    code="[SUB:NOVA][ACT:SMILE]",
                    anchor_matches=["smiled"],
                )
            ],
        )

        memory = PatternMemory.from_results(
            source_id="memory-001",
            observed_at="2026-09-22T10:00:00-07:00",
            tier1=tier1,
            tier2=tier2,
        )

        self.assertEqual(memory.original_text, tier1.original)
        self.assertNotEqual(memory.original_text, tier1.compressed)
        self.assertEqual(memory.system_codes, ("[SUB:NOVA][ACT:SMILE]",))
        self.assertEqual(PatternMemory.from_dict(memory.to_dict()), memory)

    def test_encoder_injection_embeds_original_text_with_provenance(self):
        embedder = FakeEmbedder()
        memory = self.make_memory()

        embedded = PatternEncoder(embedder).encode(memory)

        self.assertEqual(embedder.inputs, [[memory.original_text]])
        self.assertEqual(embedded.vector, (0.2, 0.4, 0.8))
        self.assertEqual(embedded.embedding_model, MINILM_MODEL_NAME)
        self.assertEqual(embedded.embedding_revision, "test-revision")
        self.assertEqual(
            embedded.source_text_sha256,
            hashlib.sha256(memory.original_text.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(EmbeddedMemory.from_dict(embedded.to_dict()), embedded)

    def test_encoder_rejects_invalid_provider_output(self):
        memory = self.make_memory()
        for vectors in ([], [[0.1, 0.2]], [[math.nan, 0.2, 0.3]]):
            with self.subTest(vectors=vectors):
                with self.assertRaises(PatternSchemaError):
                    PatternEncoder(FakeEmbedder(vectors=vectors)).encode(memory)

    def test_local_adapter_forwards_pinned_revision_and_normalizes(self):
        calls = {}

        class FakeVectors:
            def tolist(self):
                return [[0.1, 0.2, 0.3]]

        class FakeSentenceTransformer:
            def __init__(self, model_name, **kwargs):
                calls["init"] = (model_name, kwargs)

            def get_embedding_dimension(self):
                return 3

            def encode(self, texts, **kwargs):
                calls["encode"] = (texts, kwargs)
                return FakeVectors()

        fake_module = types.SimpleNamespace(
            SentenceTransformer=FakeSentenceTransformer
        )
        with mock.patch.dict("sys.modules", {"sentence_transformers": fake_module}):
            embedder = SentenceTransformerEmbedder(
                revision="pinned-commit", local_files_only=True
            )
            vectors = embedder.embed(["retained source text"])

        self.assertEqual(calls["init"][0], MINILM_MODEL_NAME)
        self.assertEqual(calls["init"][1]["revision"], "pinned-commit")
        self.assertTrue(calls["init"][1]["local_files_only"])
        self.assertTrue(calls["encode"][1]["normalize_embeddings"])
        self.assertEqual(vectors, [[0.1, 0.2, 0.3]])

    def test_node_keeps_ambiguity_and_contradiction_links_separate(self):
        ambiguity = PatternRelation(
            source_id="memory-002",
            similarity_score=0.72,
            reason="semantic match awaits calibrated policy",
            recorded_at="2026-09-22T10:05:00-07:00",
        )
        contradiction = PatternRelation(
            source_id="memory-003",
            similarity_score=0.91,
            reason="human-confirmed conflict",
            recorded_at="2026-09-22T10:06:00-07:00",
            evidence_codes=("[SUB:NOVA][ACT:REMEMBER_NOT]",),
        )
        history = PatternHistoryEntry(
            event_id="event-001",
            recorded_at="2026-09-22T10:07:00-07:00",
            action="candidate_created",
            reason="first retained instance",
            details={"source_id": "memory-001"},
        )
        node = self.make_node(
            ambiguity_links=(ambiguity,),
            contradiction_links=(contradiction,),
            history=(history,),
        )

        payload = node.to_dict()
        json.dumps(payload)
        restored = PatternNode.from_dict(payload)

        self.assertEqual(restored, node)
        self.assertEqual(restored.ambiguity_links[0].source_id, "memory-002")
        self.assertEqual(restored.contradiction_links[0].source_id, "memory-003")
        with self.assertRaises(TypeError):
            restored.anchors["new"] = 1  # type: ignore[index]
        with self.assertRaises(TypeError):
            restored.history[0].details["new"] = "value"  # type: ignore[index]

    def test_promotion_requires_three_linked_instances(self):
        with self.assertRaises(PatternSchemaError):
            self.make_node(status="pattern")

        node = self.make_node(
            status="pattern",
            instance_links=("memory-001", "memory-002", "memory-003"),
            recurrence_count=3,
        )
        self.assertEqual(node.status, "pattern")


if __name__ == "__main__":
    unittest.main()
