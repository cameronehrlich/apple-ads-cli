# Contributing

Contributions are welcome, especially reproducible endpoint fixes, official-SDK coverage updates, and safety improvements.

## Development setup

```bash
git clone https://github.com/cameronehrlich/apple-search-ads-cli.git
cd apple-search-ads-cli
uv sync --all-extras
uv run pytest -q
```

Use a focused branch and never commit credentials, private keys, account IDs, request payloads, or live advertising data.

## Architecture

The Platform API path is intentionally traceable:

```text
apple-ads-platform dependency
  -> asa_cli/platform/manifest/apple_ads_platform_v1_109_0.json
  -> asa_cli/platform/resources/<resource>.py
  -> asa_cli/platform/manifest_specs.py
  -> asa_cli/platform/command_factory.py
  -> asa_cli/platform/runtime.py
  -> asa_cli/platform/client.py
  -> asa_cli/platform/cli.py
```

Each canonical official-SDK method belongs to exactly one resource module.
Signatures, parameter locations, request models, response-model closure,
mutation classification, and context requirements come from the generated
manifest rather than handwritten copies.

The previous implementation is a compatibility boundary under `asa_cli/v5`; avoid changing its public behavior while fixing Platform API code.

## Fixing an endpoint

1. Add the smallest focused regression reproducer.
2. Determine whether the defect can affect sibling endpoints.
3. If it can, add a table-driven or manifest-wide invariant instead of testing only the reported command.
4. Fix the shared layer at the narrowest correct point.
5. Regenerate references only when their canonical inputs changed.

Common test locations:

- `tests/test_platform_manifest.py`: SDK discovery and parameter classification
- `tests/test_platform_resources_*.py`: resource registration and command help
- `tests/test_platform_command_factory.py`: request hydration, preview, mutations, and uploads
- `tests/test_platform_runtime.py`: invocation, context, errors, and serialization
- `tests/test_platform_cli_coverage.py`: complete command-tree coverage
- `tests/test_platform_workflows.py`: pagination and higher-level behavior
- `tests/test_skill_catalog.py`: generated skill/runtime reconciliation

Generated SDK models may contain `additional_properties`. Preserve the official model’s `to_dict()` semantics and test nested unknown fields when changing serialization.

For response deserialization defects, reproduce the official SDK failure before
adding compatibility behavior. A compatibility case must name the exact root
response type, field, rejected wire type/value, and Pydantic error type. Validate
a patched copy through the SDK so a known early error cannot conceal a later
unrelated failure. Add near-miss tests for adjacent fields, types, and values;
never turn an unrecognized response into empty data.

## SDK upgrades

Pin one official SDK release at a time. After changing the dependency:

```bash
uv sync --all-extras
uv run python -m asa_cli.platform.generate_manifest
uv run python scripts/generate_skill_references.py
```

Review the manifest and reference diffs. Every added, removed, or changed
official method must be classified deliberately and covered by the public
command tree. Review all response-model source/schema hash and risk-inventory
changes even when the operation count is unchanged.

## Quality gate

```bash
uv run ruff check .
uv run pytest -q
uv run python -m asa_cli.platform.generate_manifest --check
uv run python scripts/generate_skill_references.py --check
uv run python scripts/check_release.py
uv build
git diff --check
```

Live endpoint tests are supplemental evidence, not a replacement for deterministic tests. Use read-only probes where possible and sanitize all captured fixtures.

## Bug reports

Include:

- `asa version`
- Python and operating-system versions
- installation method
- exact command and exit status
- sanitized stdout/stderr
- whether the failure occurs before or after SDK invocation
- the relevant ad-account context source, without including its value

Do not post credentials, private keys, authorization headers, account IDs, campaign IDs, app IDs, or unsanitized API responses in a public issue.
