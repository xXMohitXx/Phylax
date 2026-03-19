import os
import sys

# Add project root to path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from phylax import trace, execution, Dataset, DatasetCase, run_dataset, format_report
from phylax.rag import ContextUsedRule, CitationRequiredRule

@trace(provider="mock")
def execute_pipeline(query: str) -> str:
    """RAG baseline response pipeline."""
    return f"Response based on query: {query}. The context confirms the details. [Source 1]"

def main():
    print("=== RAG Pipeline Template ===")
    
    with execution():
        ans = execute_pipeline("What is ML?")
        print(f"Pipeline Result: {ans}")

if __name__ == "__main__":
    main()
