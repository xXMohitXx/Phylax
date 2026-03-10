"""
Dataset loader — Parse YAML contract files into Dataset models.

Supported format:
    dataset: my_dataset
    cases:
      - input: "user prompt"
        expectations:
          must_include: ["word"]
          must_not_include: ["bad"]
          max_latency_ms: 3000
          min_tokens: 20
"""
from pathlib import Path
from typing import Union

import yaml

from phylax._internal.datasets.schema import Dataset, DatasetCase


def load_dataset(path: Union[str, Path]) -> Dataset:
    """Load a dataset contract from a YAML file.

    Args:
        path: Path to the YAML contract file.

    Returns:
        A validated Dataset model.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is malformed or missing required fields.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    if not path.suffix in (".yaml", ".yml"):
        raise ValueError(f"Dataset file must be .yaml or .yml, got: {path.suffix}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Dataset file must contain a YAML mapping, got: {type(raw).__name__}")

    if "dataset" not in raw:
        raise ValueError("Dataset file must have a 'dataset' field with the dataset name")

    if "cases" not in raw:
        raise ValueError("Dataset file must have a 'cases' field with test cases")

    if not isinstance(raw["cases"], list):
        raise ValueError(f"'cases' must be a list, got: {type(raw['cases']).__name__}")

    if len(raw["cases"]) == 0:
        raise ValueError("'cases' must contain at least one test case")

    # Parse cases
    cases = []
    for i, case_raw in enumerate(raw["cases"]):
        if not isinstance(case_raw, dict):
            raise ValueError(f"Case {i} must be a mapping, got: {type(case_raw).__name__}")

        if "input" not in case_raw:
            raise ValueError(f"Case {i} must have an 'input' field")

        case = DatasetCase(
            input=str(case_raw["input"]),
            expectations=case_raw.get("expectations", {}),
            name=case_raw.get("name"),
            metadata=case_raw.get("metadata"),
        )
        cases.append(case)

    return Dataset(
        dataset=str(raw["dataset"]),
        cases=cases,
        version=raw.get("version"),
        description=raw.get("description"),
    )
