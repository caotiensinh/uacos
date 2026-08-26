"""AI-agent orchestration contracts for UACOS.

UACOS coordinates agents and code workflows, but it is not itself a general-purpose
agent. This package defines safe, finite DevOps-style loops around existing UACOS
context, patch, test, rollback, and reporting primitives.
"""

from .contract import build_orchestration_plan, get_orchestration_contract, next_loop_decision

__all__ = ["build_orchestration_plan", "get_orchestration_contract", "next_loop_decision"]
