"""
Test suite for Phylax Guardrail Packs (Phase 6).

Tests:
    - Public API imports
    - Built-in pack contents (safety, quality, compliance)
    - Pack registry (list, get, unknown)
    - to_expectations() conversion
    - apply_pack() merging
    - Integration with dataset executor
"""
import pytest


# ===========================================================================
# PUBLIC API IMPORT TESTS
# ===========================================================================

class TestGuardrailPublicAPI:
    """All guardrail symbols must be importable from phylax directly."""

    def test_import_guardrail_pack(self):
        from phylax import GuardrailPack
        assert GuardrailPack is not None

    def test_import_get_pack(self):
        from phylax import get_pack
        assert callable(get_pack)

    def test_import_list_packs(self):
        from phylax import list_packs
        assert callable(list_packs)

    def test_import_apply_pack(self):
        from phylax import apply_pack
        assert callable(apply_pack)

    def test_import_safety_pack(self):
        from phylax import safety_pack
        assert callable(safety_pack)

    def test_import_quality_pack(self):
        from phylax import quality_pack
        assert callable(quality_pack)

    def test_import_compliance_pack(self):
        from phylax import compliance_pack
        assert callable(compliance_pack)


# ===========================================================================
# BUILT-IN PACK TESTS
# ===========================================================================

class TestSafetyPack:
    """Safety guardrail pack tests."""

    def test_safety_pack_name(self):
        from phylax import safety_pack
        pack = safety_pack()
        assert pack.name == "safety"

    def test_safety_pack_has_rules(self):
        from phylax import safety_pack
        pack = safety_pack()
        assert len(pack.rules) >= 3

    def test_safety_pack_blocks_hate(self):
        from phylax import safety_pack
        pack = safety_pack()
        expectations = pack.to_expectations()
        assert "must_not_include" in expectations
        # Should block hate-related terms
        blocked = expectations["must_not_include"]
        assert any("kill" in term.lower() for term in blocked)

    def test_safety_pack_blocks_pii(self):
        from phylax import safety_pack
        pack = safety_pack()
        expectations = pack.to_expectations()
        blocked = expectations["must_not_include"]
        assert any("ssn" in term.lower() for term in blocked)

    def test_safety_pack_frozen(self):
        from phylax import safety_pack
        pack = safety_pack()
        with pytest.raises(Exception):
            pack.name = "modified"


class TestQualityPack:
    """Quality guardrail pack tests."""

    def test_quality_pack_name(self):
        from phylax import quality_pack
        pack = quality_pack()
        assert pack.name == "quality"

    def test_quality_pack_min_tokens(self):
        from phylax import quality_pack
        pack = quality_pack()
        expectations = pack.to_expectations()
        assert "min_tokens" in expectations
        assert expectations["min_tokens"] >= 5

    def test_quality_pack_latency(self):
        from phylax import quality_pack
        pack = quality_pack()
        expectations = pack.to_expectations()
        assert "max_latency_ms" in expectations

    def test_quality_pack_no_placeholders(self):
        from phylax import quality_pack
        pack = quality_pack()
        expectations = pack.to_expectations()
        blocked = expectations.get("must_not_include", [])
        assert any("todo" in term.lower() for term in blocked)


class TestCompliancePack:
    """Compliance guardrail pack tests."""

    def test_compliance_pack_name(self):
        from phylax import compliance_pack
        pack = compliance_pack()
        assert pack.name == "compliance"

    def test_compliance_blocks_financial_advice(self):
        from phylax import compliance_pack
        pack = compliance_pack()
        expectations = pack.to_expectations()
        blocked = expectations["must_not_include"]
        assert any("invest" in term.lower() for term in blocked)

    def test_compliance_blocks_medical(self):
        from phylax import compliance_pack
        pack = compliance_pack()
        expectations = pack.to_expectations()
        blocked = expectations["must_not_include"]
        assert any("diagnosis" in term.lower() for term in blocked)


# ===========================================================================
# REGISTRY TESTS
# ===========================================================================

class TestPackRegistry:
    """Pack registry tests."""

    def test_list_packs(self):
        from phylax import list_packs
        packs = list_packs()
        assert "safety" in packs
        assert "quality" in packs
        assert "compliance" in packs

    def test_get_pack_safety(self):
        from phylax import get_pack
        pack = get_pack("safety")
        assert pack.name == "safety"

    def test_get_pack_quality(self):
        from phylax import get_pack
        pack = get_pack("quality")
        assert pack.name == "quality"

    def test_get_pack_compliance(self):
        from phylax import get_pack
        pack = get_pack("compliance")
        assert pack.name == "compliance"

    def test_get_pack_unknown(self):
        from phylax import get_pack
        with pytest.raises(ValueError, match="Unknown guardrail pack"):
            get_pack("nonexistent")


# ===========================================================================
# APPLY PACK TESTS
# ===========================================================================

class TestApplyPack:
    """apply_pack() merging tests."""

    def test_apply_to_empty(self):
        from phylax import safety_pack, apply_pack
        pack = safety_pack()
        merged = apply_pack(pack, {})
        assert "must_not_include" in merged
        assert len(merged["must_not_include"]) > 0

    def test_apply_preserves_existing(self):
        from phylax import quality_pack, apply_pack
        pack = quality_pack()
        existing = {"must_include": ["hello"], "must_not_include": ["goodbye"]}
        merged = apply_pack(pack, existing)
        assert "hello" in merged["must_include"]
        assert "goodbye" in merged["must_not_include"]

    def test_apply_merges_must_not_include(self):
        from phylax import safety_pack, apply_pack
        pack = safety_pack()
        existing = {"must_not_include": ["custom_forbidden"]}
        merged = apply_pack(pack, existing)
        assert "custom_forbidden" in merged["must_not_include"]
        # Should also have safety pack items
        assert len(merged["must_not_include"]) > 1


# ===========================================================================
# INTEGRATION TESTS
# ===========================================================================

class TestGuardrailIntegration:
    """Integration with dataset executor."""

    def test_safety_pack_catches_harmful_content(self):
        from phylax import Dataset, DatasetCase, run_dataset, safety_pack
        pack = safety_pack()
        expectations = pack.to_expectations()

        ds = Dataset(dataset="safety_test", cases=[
            DatasetCase(input="test", expectations=expectations),
        ])

        # Function that returns harmful content
        result = run_dataset(ds, lambda x: "I hate everything and want to kill")
        assert not result.all_passed
        assert result.failed_cases == 1

    def test_safety_pack_passes_clean_content(self):
        from phylax import Dataset, DatasetCase, run_dataset, safety_pack
        pack = safety_pack()
        expectations = pack.to_expectations()

        ds = Dataset(dataset="safety_test", cases=[
            DatasetCase(input="test", expectations=expectations),
        ])

        # Function that returns clean content
        result = run_dataset(ds, lambda x: "Here is a helpful and friendly response about your question.")
        assert result.all_passed

    def test_quality_pack_catches_short_response(self):
        from phylax import Dataset, DatasetCase, run_dataset, quality_pack
        pack = quality_pack()
        expectations = pack.to_expectations()

        ds = Dataset(dataset="quality_test", cases=[
            DatasetCase(input="test", expectations=expectations),
        ])

        # Function that returns too-short response
        result = run_dataset(ds, lambda x: "OK")
        assert not result.all_passed
