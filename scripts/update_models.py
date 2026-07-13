#!/usr/bin/env python3
"""Print or refresh the model registry (configs/models.yaml).

Without args it prints the resolved registry. With --write it overwrites
configs/models.yaml with the built-in defaults (useful after upgrades).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.llm.model_registry import DEFAULT_REGISTRY, ModelRegistry
from agent.utils.yaml_lite import load_file

CONFIG = os.path.join(os.path.dirname(__file__), "..", "configs", "models.yaml")


def main(argv=None):
    write = "--write" in (argv or sys.argv[1:])
    current = load_file(CONFIG) if os.path.exists(CONFIG) else {}
    reg = ModelRegistry(current or DEFAULT_REGISTRY)
    print("Providers:")
    for p in reg.list_providers():
        print(f"  {p:10s} default={reg.default_model(p)} base={reg.base_url(p)}")
    print("Weak-device models:", reg.weak)
    if write:
        import json

        with open(CONFIG, "w", encoding="utf-8") as fh:
            fh.write(_dump(DEFAULT_REGISTRY))
        print(f"\nWrote {CONFIG}")


def _dump(obj) -> str:
    import yaml

    try:
        return yaml.safe_dump(obj, sort_keys=False)
    except Exception:
        import json

        return json.dumps(obj, indent=2)


if __name__ == "__main__":
    main()
