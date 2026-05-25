import yaml
from pathlib import Path

_POLICY_PATH = Path(__file__).parent.parent / "config" / "shopmate_policy.yaml"

def load_policy() -> dict:
    with open(_POLICY_PATH, "r") as f:
        return yaml.safe_load(f)

policy = load_policy()
