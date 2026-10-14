#!/usr/bin/env python3
"""Record the reviewed stage-02/03 default-model drift; never edit live config."""
import argparse
import copy
import json
import re
import tomllib
from pathlib import Path

import run_one as r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--historical-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    original = r.load(args.freeze)
    amended = copy.deepcopy(original)
    config_path = Path.home() / ".codex/config.toml"
    entries = [e for e in amended["controls"]["common_files"] if e["path"] == str(config_path)]
    if len(entries) != 1 or entries[0]["mode"] != "redacted_toml":
        raise ValueError("Expected one original redacted user-config fingerprint")
    original_hash = entries[0]["sha256"]
    current = r.redact(tomllib.loads(config_path.read_text()))
    historical = r.redact(tomllib.loads(args.historical_config.read_text()))
    reconstructed = copy.deepcopy(current)
    changes = {}
    for key in ("model", "model_reasoning_effort"):
        old, new = historical[key], current[key]
        if not all(isinstance(v, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", v) for v in (old, new)):
            raise ValueError("Unexpected value in the two safe default fields")
        reconstructed[key] = old
        changes[key] = {"original": old, "current": new}
    if r.digest(r.canonical(reconstructed)) != original_hash:
        raise ValueError("Two-default reconstruction does not match the exact original freeze")
    current_hash = r.digest(r.canonical(current))
    if current_hash == original_hash:
        raise ValueError("No configuration drift to amend")
    for entry in amended["controls"]["common_files"]:
        if entry["path"] != str(config_path):
            r.verify_file(entry)
    entries[0]["sha256"] = current_hash
    amended["amendment"] = {
        "amended_at": r.now(), "applies_to_stages": ["02", "03"],
        "original_freeze": r.fingerprint(args.freeze),
        "historical_config_source": r.fingerprint(args.historical_config, "redacted_toml"),
        "original_redacted_config_sha256": original_hash,
        "current_redacted_config_sha256": current_hash,
        "changed_defaults": changes,
        "proof": "Replacing only the two current defaults with historical values exactly reproduces the original redacted hash; every other represented value is unchanged",
        "explicit_experimental_overrides_unchanged": {"model": "gpt-6-astra", "reasoning_effort": "ultra"},
        "reviewer": "parent-orchestrator",
        "scope": "Accept these two inherited defaults for stages 02/03 because run_one.py explicitly overrides both. Preserve all original setup provenance, allocation, scientific inputs, and controls.",
        "not_a_new_all_six_setup_freeze": True,
        "limitations": "Historical full pre-freeze bytes were unavailable; exact redacted-state reconstruction used an older backup. Writer/reason and intermediate configuration history are unknown. Existing redaction intentionally excludes secret-bearing values; those were not compared."
    }
    if r.fingerprint(config_path, "redacted_toml")["sha256"] != current_hash:
        raise ValueError("Live configuration changed during amendment review")
    with args.output.open("x") as stream:
        json.dump(amended, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "bounded_amendment_written", "output": r.fingerprint(args.output),
                      "changed_defaults": changes, "original_freeze_modified": False,
                      "live_configuration_modified": False, "experimental_overrides_changed": False}, indent=2))


if __name__ == "__main__":
    main()
