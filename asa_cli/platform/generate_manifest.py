"""Generate the committed Apple Ads Platform SDK manifest and its schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asa_cli.platform.manifest_discovery import MANIFEST_SCHEMA, discover_manifest

MANIFEST_DIRECTORY = Path(__file__).with_name("manifest")
MANIFEST_PATH = MANIFEST_DIRECTORY / "apple_ads_platform_v1_109_0.json"
SCHEMA_PATH = MANIFEST_DIRECTORY / "apple_ads_platform_manifest.schema.json"


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def generate(*, check: bool = False) -> bool:
    """Write generated artifacts, or return whether committed artifacts are current."""

    expected = {
        MANIFEST_PATH: _render(discover_manifest()),
        SCHEMA_PATH: _render(MANIFEST_SCHEMA),
    }
    current = {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in expected
    }
    matches = all(current[path] == content for path, content in expected.items())
    if check:
        return matches

    MANIFEST_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if committed artifacts differ from the pinned SDK",
    )
    args = parser.parse_args()
    if args.check and not generate(check=True):
        parser.error("committed SDK manifest artifacts are stale; regenerate them")
    if not args.check:
        generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
