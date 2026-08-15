#!/usr/bin/env python3
"""Generate or verify progressive-disclosure skill references."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _command_catalog import DEFAULT_MANIFEST, REFERENCES_DIR, load_manifest, render_reference_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=REFERENCES_DIR)
    parser.add_argument("--check", action="store_true", help="Fail if generated references differ")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rendered = render_reference_files(load_manifest(args.manifest))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    stale: list[str] = []
    for filename, expected in rendered.items():
        path = args.output_dir / filename
        if args.check:
            actual = path.read_text() if path.exists() else None
            if actual != expected:
                stale.append(filename)
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(expected)

    if stale:
        print("Generated skill references are stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print(f"Generated skill references are current ({len(rendered)} files).")
    else:
        print(f"Generated {len(rendered)} skill reference files in {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
