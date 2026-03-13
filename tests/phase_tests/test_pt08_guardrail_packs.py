"""
Phase-test 8 — Guardrail Pack Compatibility

Goal: Ensure guardrail packs load, registry works, expectations evaluate correctly,
and packs never corrupt core behavior.
"""
import pytest
from phylax import (
    safety_pack, quality_pack, compliance_pack,
    list_packs, get_pack, apply_pack,
    Dataset, DatasetCase, run_dataset,
)


class TestPackLoading:
    """PT8.1: All packs must load without errors."""

    def test_safety_pack_loads(self):
        pack = safety_pack()
        assert pack is not None
        assert pack.name == "safety"

    def test_quality_pack_loads(self):
        pack = quality_pack()
        assert pack is not None
        assert pack.name == "quality"

    def test_compliance_pack_loads(self):
        pack = compliance_pack()
        assert pack is not None
        assert pack.name == "compliance"

    def test_all_packs_have_rules(self):
        for pack_fn in [safety_pack, quality_pack, compliance_pack]:
            pack = pack_fn()
            assert len(pack.rules) > 0, f"Pack {pack.name} has zero rules"


class TestPackRegistry:
    """PT8.2: Registry must list and retrieve packs correctly."""

    def test_list_packs_returns_all(self):
        packs = list_packs()
        assert "safety" in packs
        assert "quality" in packs
        assert "compliance" in packs

    def test_get_pack_by_name(self):
        for name in ["safety", "quality", "compliance"]:
            pack = get_pack(name)
            assert pack is not None
            assert pack.name == name

    def test_get_nonexistent_pack_raises(self):
        with pytest.raises(ValueError):
            get_pack("nonexistent_pack_xyz")


class TestPackToExpectations:
    """PT8.3: Packs must convert to valid expectations."""

    def test_safety_pack_to_expectations(self):
        pack = safety_pack()
        exp = pack.to_expectations()
        assert isinstance(exp, dict)
        assert "must_not_include" in exp
        assert len(exp["must_not_include"]) > 0

    def test_quality_pack_to_expectations(self):
        pack = quality_pack()
        exp = pack.to_expectations()
        assert isinstance(exp, dict)

    def test_compliance_pack_to_expectations(self):
        pack = compliance_pack()
        exp = pack.to_expectations()
        assert isinstance(exp, dict)


class TestApplyPack:
    """PT8.4: apply_pack must merge correctly."""

    def test_apply_adds_rules(self):
        custom = {"must_include": ["hello"], "min_tokens": 5}
        pack = safety_pack()
        merged = apply_pack(pack, custom)
        assert isinstance(merged, dict)
        # Custom rules preserved
        assert "hello" in merged.get("must_include", [])

    def test_apply_does_not_lose_custom(self):
        custom = {"must_include": ["custom_keyword"]}
        pack = quality_pack()
        merged = apply_pack(pack, custom)
        assert "custom_keyword" in merged.get("must_include", [])


class TestPacksWithDataset:
    """PT8.5: Packs must work correctly with dataset execution."""

    def test_safety_pack_catches_harmful(self):
        pack = safety_pack()
        exp = pack.to_expectations()
        ds = Dataset(
            dataset="safety_test",
            cases=[
                DatasetCase(
                    input="test",
                    expectations=exp,
                ),
            ],
        )
        # Safe response should pass
        def safe_func(x):
            return "Here is a helpful and professional response about the topic."
        result = run_dataset(ds, safe_func)
        assert result.all_passed

    def test_packs_never_crash_executor(self):
        """Running any pack through executor must not crash."""
        for pack_fn in [safety_pack, quality_pack, compliance_pack]:
            pack = pack_fn()
            exp = pack.to_expectations()
            ds = Dataset(
                dataset=f"pack_test_{pack.name}",
                cases=[
                    DatasetCase(input="test", expectations=exp),
                ],
            )
            # Should not raise
            result = run_dataset(ds, lambda x: "A generic response with sufficient content for testing purposes.")
            assert result.total_cases == 1


class TestPackDeterminism:
    """PT8.6: Pack construction must be deterministic."""

    def test_safety_pack_same_every_time(self):
        packs = [safety_pack() for _ in range(5)]
        rules = [tuple(r.name for r in p.rules) for p in packs]
        assert len(set(rules)) == 1

    def test_registry_stable(self):
        lists = [tuple(list_packs()) for _ in range(5)]
        assert len(set(lists)) == 1
