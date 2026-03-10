"""
Dataset contract schema — Pydantic models for dataset-driven testing.

Models:
    DatasetCase — A single test case with input and expected behavior.
    Dataset — A named collection of test cases loaded from YAML.
    CaseResult — Result of running a single test case.
    DatasetResult — Aggregate result of running all cases in a dataset.
"""
from pydantic import BaseModel, Field
from typing import Optional
import uuid


class DatasetCase(BaseModel):
    """A single test case in a dataset contract.

    Attributes:
        input: The input string (prompt) to send to the function under test.
        expectations: Dictionary of expectation rules to enforce.
            Supported keys: must_include, must_not_include, max_latency_ms, min_tokens
        name: Optional human-readable name for the test case.
        metadata: Optional extra metadata for the case.
    """
    input: str
    expectations: dict = Field(default_factory=dict)
    name: Optional[str] = None
    metadata: Optional[dict] = None

    model_config = {"frozen": True}


class Dataset(BaseModel):
    """A named collection of test cases loaded from a YAML contract file.

    Attributes:
        dataset: Name identifier for this dataset.
        cases: List of DatasetCase entries.
        version: Optional version string.
        description: Optional description.
    """
    dataset: str
    cases: list[DatasetCase]
    version: Optional[str] = None
    description: Optional[str] = None

    model_config = {"frozen": True}


class CaseResult(BaseModel):
    """Result of evaluating a single dataset case.

    Attributes:
        case_index: 0-based index of the case in the dataset.
        case_name: Name of the case (or auto-generated from index).
        input: The input that was tested.
        output: The output returned by the function under test.
        passed: Whether all expectations were met.
        violations: List of violation messages (empty if passed).
        latency_ms: Execution time in milliseconds.
    """
    case_index: int
    case_name: str
    input: str
    output: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    latency_ms: float = 0.0

    model_config = {"frozen": True}


class DatasetResult(BaseModel):
    """Aggregate result of running all cases in a dataset.

    Attributes:
        dataset_name: Name of the dataset.
        run_id: Unique identifier for this run.
        total_cases: Number of cases executed.
        passed_cases: Number of cases that passed.
        failed_cases: Number of cases that failed.
        results: List of individual CaseResult entries.
    """
    dataset_name: str
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_cases: int
    passed_cases: int
    failed_cases: int
    results: list[CaseResult]

    model_config = {"frozen": True}

    @property
    def all_passed(self) -> bool:
        """True if every case passed."""
        return self.failed_cases == 0
