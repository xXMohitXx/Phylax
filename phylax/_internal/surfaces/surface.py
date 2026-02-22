"""
Surface Abstraction Layer — Core Models

Axis 2 Phase 2.0: Mandatory Foundation

All enforcement inputs reduce to a Surface:
    Surface { id, type, raw_payload, metadata }

The engine must not know whether it is enforcing text, JSON, tool calls,
execution traces, or cross-run snapshots. It only receives structured
values and explicit expectations.

Design rules:
- Raw payload is preserved as-is (no normalization, no transformation)
- Deterministic serialization (no hidden mutation)
- Verdicts remain binary: PASS / FAIL
"""

from abc import ABC, abstractmethod
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field
import uuid


# ─── Surface Types ───────────────────────────────────────────────────────────

SurfaceType = Literal[
    "text_output",
    "structured_output",
    "tool_calls",
    "execution_trace",
    "cross_run_snapshot",
]


# ─── Core Models ─────────────────────────────────────────────────────────────

class Surface(BaseModel):
    """
    Generic enforcement surface.

    All enforcement inputs reduce to this model. The engine does not
    know or care what the surface represents — it only evaluates
    explicit rules against the raw_payload.

    Attributes:
        id: Unique surface ID (auto-generated UUID)
        type: Surface type (text_output, structured_output, etc.)
        raw_payload: Original payload, preserved without modification
        metadata: Optional user-defined metadata
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: SurfaceType
    raw_payload: Any
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        frozen = True  # Immutable once created


class SurfaceRuleResult:
    """
    Result of evaluating a single surface rule.

    Attributes:
        passed: Whether the rule passed
        rule_name: Name of the rule that produced this result
        violation_message: Human-readable violation description (empty if passed)
    """

    def __init__(
        self,
        passed: bool,
        rule_name: str,
        violation_message: str = "",
    ):
        self.passed = passed
        self.rule_name = rule_name
        self.violation_message = violation_message

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"SurfaceRuleResult({self.rule_name}: {status})"


class SurfaceVerdict(BaseModel):
    """
    Verdict for a surface enforcement evaluation.

    Identical semantics to Verdict: binary PASS/FAIL, no scores, no partial.

    Attributes:
        status: "pass" or "fail" — only two values, ever
        violations: List of human-readable violation messages
        surface_id: ID of the surface that was evaluated
    """
    status: Literal["pass", "fail"]
    violations: list[str] = []
    surface_id: str = ""

    class Config:
        frozen = True


# ─── Abstract Base Classes ───────────────────────────────────────────────────

class SurfaceRule(ABC):
    """
    Base class for surface enforcement rules.

    Unlike text-based Rule (which takes response_text + latency_ms),
    SurfaceRule operates on a generic Surface. This allows enforcement
    over any payload type.

    Subclasses must implement:
        evaluate(surface: Surface) → SurfaceRuleResult
    """

    name: str = "surface_rule"

    @abstractmethod
    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        """
        Evaluate the rule against a surface.

        Args:
            surface: The Surface to evaluate

        Returns:
            SurfaceRuleResult indicating pass/fail and violation details
        """
        pass


class SurfaceAdapter(ABC):
    """
    Base class for surface adapters.

    Adapters convert raw data into a Surface. They must preserve the
    original raw payload without normalization or transformation.

    Subclasses must implement:
        adapt(raw_data, **kwargs) → Surface
    """

    surface_type: SurfaceType = "text_output"

    @abstractmethod
    def adapt(self, raw_data: Any, **kwargs) -> Surface:
        """
        Convert raw data into a Surface.

        Args:
            raw_data: The raw payload to wrap

        Returns:
            Surface with raw_payload set to raw_data (preserved as-is)
        """
        pass


# ─── Surface Evaluator ──────────────────────────────────────────────────────

class SurfaceEvaluator:
    """
    Evaluates a set of surface rules against a Surface.

    Produces a SurfaceVerdict (binary PASS/FAIL).
    All rules are evaluated — no short-circuit.

    Usage:
        evaluator = SurfaceEvaluator()
        evaluator.add_rule(FieldExistsRule("data.name"))
        evaluator.add_rule(TypeEnforcementRule("data.count", "number"))
        verdict = evaluator.evaluate(surface)
    """

    def __init__(self):
        self._rules: list[SurfaceRule] = []

    def add_rule(self, rule: SurfaceRule) -> "SurfaceEvaluator":
        """Add a rule. Returns self for chaining."""
        self._rules.append(rule)
        return self

    @property
    def rules(self) -> list[SurfaceRule]:
        """List of registered rules."""
        return list(self._rules)

    def evaluate(self, surface: Surface) -> SurfaceVerdict:
        """
        Evaluate all rules against the surface.

        All rules are evaluated (no short-circuit).

        Args:
            surface: The Surface to evaluate

        Returns:
            SurfaceVerdict with binary status and violation list
        """
        violations: list[str] = []

        for rule in self._rules:
            result = rule.evaluate(surface)
            if not result.passed:
                violations.append(
                    f"[{result.rule_name}] {result.violation_message}"
                )

        return SurfaceVerdict(
            status="fail" if violations else "pass",
            violations=violations,
            surface_id=surface.id,
        )


# ─── Surface Registry ───────────────────────────────────────────────────────

class SurfaceRegistry:
    """
    Registry for surface types.

    Allows registering and looking up surface type metadata.
    Pre-registers all built-in surface types on creation.

    Usage:
        registry = SurfaceRegistry()
        registry.register("custom_type", description="My custom surface")
        assert registry.exists("text_output")
    """

    def __init__(self):
        self._surfaces: dict[str, dict[str, str]] = {}
        # Pre-register built-in surface types
        self.register("text_output", description="Plain text LLM response")
        self.register("structured_output", description="JSON/dict structured output")
        self.register("tool_calls", description="Tool/function call event sequence")
        self.register("execution_trace", description="Multi-step execution trace")
        self.register("cross_run_snapshot", description="Cross-run stability snapshot")

    def register(self, surface_type: str, description: str = "") -> "SurfaceRegistry":
        """
        Register a surface type.

        Args:
            surface_type: Unique surface type identifier
            description: Human-readable description

        Raises:
            ValueError: If surface type is already registered
        """
        if surface_type in self._surfaces:
            raise ValueError(f"Surface type already registered: {surface_type}")
        self._surfaces[surface_type] = {"description": description}
        return self

    def exists(self, surface_type: str) -> bool:
        """Check if a surface type is registered."""
        return surface_type in self._surfaces

    def get(self, surface_type: str) -> dict[str, str]:
        """
        Get surface type metadata.

        Raises:
            KeyError: If surface type is not registered
        """
        if surface_type not in self._surfaces:
            raise KeyError(f"Unknown surface type: {surface_type}")
        return self._surfaces[surface_type]

    def list_types(self) -> list[str]:
        """List all registered surface types."""
        return list(self._surfaces.keys())

    def clear(self) -> None:
        """Clear all registered types (testing only)."""
        self._surfaces.clear()


# ─── Global Registry ─────────────────────────────────────────────────────────

_global_registry: Optional[SurfaceRegistry] = None


def get_registry() -> SurfaceRegistry:
    """Get or create the global surface registry singleton."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SurfaceRegistry()
    return _global_registry
