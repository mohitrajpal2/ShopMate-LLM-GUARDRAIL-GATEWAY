import os
import yaml

_POLICY_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "shopmate_policy.yaml")

with open(_POLICY_PATH) as f:
    POLICY: dict = yaml.safe_load(f)


def get_role_policy(role: str) -> dict:
    return POLICY["roles"].get(role, {})


def get_internal_fields() -> list[str]:
    return POLICY["internal_data"]["never_expose"]


def get_escalation_policy() -> dict:
    return POLICY["escalation"]
