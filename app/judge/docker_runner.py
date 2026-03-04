"""
Run user code in isolated Docker container only.
- Disable network
- Limit memory, CPU, timeout
Never run user code directly on server.
"""

from typing import Any


def run_judge(
    code: str,
    language: str,
    test_cases: list[dict],
    time_limit_ms: int,
    memory_limit_mb: int,
) -> list[dict[str, Any]]:
    """
    Execute code in Docker for each test case. Returns list of result dicts.
    Each dict: status, output, error, time_ms, memory_mb, test_case_id, order.
    """
    results = []
    # Stub: real implementation must use docker SDK to create container with
    # network_disabled=True, memory limit, cpu quota, timeout.
    # Do NOT use subprocess with user code or eval().
    for i, tc in enumerate(test_cases):
        results.append(
            {
                "status": "accepted",
                "output": "",
                "error": None,
                "time_ms": 0,
                "memory_mb": 0.0,
                "test_case_id": tc.get("id", ""),
                "order": tc.get("order", i),
            }
        )
    return results
