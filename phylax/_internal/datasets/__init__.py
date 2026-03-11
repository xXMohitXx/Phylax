"""
Phylax Dataset Contracts — Batch test LLM behavior with YAML contracts.

This module provides:
    - Dataset/DatasetCase schema for defining test cases
    - YAML loader for reading contract files
    - Executor for running cases against a callable
    - Reporter for formatting results
    - Diff engine for comparing runs
"""
from phylax._internal.datasets.schema import Dataset, DatasetCase, DatasetResult, CaseResult
from phylax._internal.datasets.loader import load_dataset
from phylax._internal.datasets.executor import run_dataset
from phylax._internal.datasets.reporter import format_report, format_json_report
from phylax._internal.datasets.diff import (
    CaseDiff, DatasetDiff, diff_runs, format_diff_report, format_diff_json,
)

__all__ = [
    "Dataset",
    "DatasetCase",
    "DatasetResult",
    "CaseResult",
    "load_dataset",
    "run_dataset",
    "format_report",
    "format_json_report",
    "CaseDiff",
    "DatasetDiff",
    "diff_runs",
    "format_diff_report",
    "format_diff_json",
]
