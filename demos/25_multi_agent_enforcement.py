"""
Demo 25: Multi-Agent Enforcement
================================
Demonstrate deterministic validation for multi-agent workflows.

Features demonstrated:
    - ToolSequenceRule (relaxed and strict ordering)
    - ToolPresenceValidator (must/must-not call)
    - AgentStepValidator (step count and required types)
"""
from phylax.agents import (
    ToolSequenceRule,
    ToolPresenceValidator,
    AgentStepValidator,
)

def main():
    print("=" * 60)
    print("Demo 25: Multi-Agent Enforcement")
    print("=" * 60)

    # 1. Tool Sequence Validation
    print("\n--- 1. ToolSequenceRule ---")
    sequence_rule = ToolSequenceRule(required_sequence=["search_db", "format_data", "send_response"], strict=False)
    
    # Valid execution path
    valid_calls = [
        {"tool_name": "search_db"},
        {"tool_name": "log_event"},  # Extra tool allowed in relaxed mode
        {"tool_name": "format_data"},
        {"tool_name": "send_response"},
    ]
    res1 = sequence_rule.evaluate(valid_calls)
    print(f"Valid sequence evaluation: {'✅ PASS' if res1.passed else '❌ FAIL'}")

    # Invalid execution path
    invalid_calls = [
        {"tool_name": "format_data"},
        {"tool_name": "search_db"},
        {"tool_name": "send_response"},
    ]
    res2 = sequence_rule.evaluate(invalid_calls)
    print(f"Out-of-order evaluation: {'✅ PASS' if res2.passed else '❌ FAIL'}")
    if not res2.passed:
        print(f"  Violation: {res2.violations[0]}")

    # 2. Tool Presence Validation
    print("\n--- 2. ToolPresenceValidator ---")
    presence_rule = ToolPresenceValidator(must_call=["auth_check"], must_not_call=["delete_database"])
    
    # Violating path
    danger_calls = [
        {"tool_name": "auth_check"},
        {"tool_name": "delete_database"},
    ]
    res3 = presence_rule.evaluate(danger_calls)
    print(f"Dangerous tool call check: {'✅ PASS' if res3.passed else '❌ FAIL'}")
    if not res3.passed:
        print(f"  Violation: {res3.violations[0]}")

    # 3. Agent Step Validation
    print("\n--- 3. AgentStepValidator ---")
    step_validator = AgentStepValidator(min_steps=2, max_steps=4, required_step_types=["planner", "executor"])
    
    workflow_steps = [
        {"type": "planner", "status": "pass", "name": "plan_workflow"},
        {"type": "executor", "status": "fail", "name": "execute_query"},
        {"type": "responder", "status": "pass", "name": "respond_user"},
    ]
    res4 = step_validator.evaluate(workflow_steps)
    print(f"Workflow step boundary evaluation: {'✅ PASS' if res4.passed else '❌ FAIL'}")
    if not res4.passed:
        # It will fail because executor node failed inside the graph!
        print(f"  Violation: {res4.violations[0]}")

if __name__ == "__main__":
    main()
