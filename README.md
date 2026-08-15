# Apple Ads CLI

A complete command-line wrapper for Apple's official Apple Ads Platform Python SDK, with the previous Campaign Management API v5 implementation preserved under an explicit namespace.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apple Ads Platform SDK 1.109.0](https://img.shields.io/badge/Apple%20Ads%20Platform%20SDK-1.109.0-black.svg)](https://github.com/apple/apple-ads-platform-api-python/releases/tag/v1.109.0)
[![CI](https://github.com/cameronehrlich/apple-search-ads-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/cameronehrlich/apple-search-ads-cli/actions/workflows/ci.yml)

## Command architecture

The CLI has three deliberately separate surfaces:

| Surface | Purpose | Example |
|---|---|---|
| `asa <resource> <action>` | Default Platform API v1 wrappers using Apple's SDK | `asa campaigns query --file query.json` |
| `asa workflows ...` | Selected opinionated behavior above the SDK layer | `asa workflows campaigns audit` |
| `asa v5 ...` | Frozen compatibility surface for the previous implementation | `asa v5 campaigns list` |

Platform API v1 covers all **99 canonical SDK methods** across **24 resource families**. Each method appears in exactly one explicit resource module, and automated drift tests compare the registered CLI against the pinned SDK manifest.

## Install

Python 3.12 or newer is required because the official SDK requires it.

```bash
git clone https://github.com/cameronehrlich/apple-search-ads-cli.git
cd apple-search-ads-cli

uv sync --all-extras
uv run asa --help
```

An editable pip install also works:

```bash
python3.12 -m pip install -e '.[dev]'
asa --help
```

## Configure

```bash
asa config setup
asa config show
asa config test
```

Most ad-serving resource requests require an ad-account context; a small number of access, account-creation, and shared-budget methods declare none or optional context. When required, supply it in one of three ways, in precedence order:

1. `--ad-account AD_ACCOUNT_ID`
2. `ASA_AD_ACCOUNT_ID`
3. `ad_account_id` saved by `asa config setup`

The legacy v5 organization ID is intentionally not used as the Platform API ad-account ID.

Credentials use Apple's client ID, team ID, key ID, and EC private key. The credentials file is saved with mode `0600`.

## Platform API v1

Every resource exposes its own help and every endpoint maps to exactly one official SDK call:

```bash
asa campaigns --help
asa campaigns get --id CAMPAIGN_ID
asa campaigns query --file query.json

asa ad-groups query --file query.json
asa keywords bulk-create --file keywords.json
asa negative-keywords query --file query.json

asa insights impression-share --file impression-share.json
asa insights search-term-popularity --file popularity.json

asa recommendations daily-budget-query --file recommendations.json
asa suggestions keywords --file suggestions.json

asa reports-apps campaign --file report.json
asa reports-business-brands search-term --file report.json
```

Run `--help` on the concrete command for its exact scalar options, request-file requirement, account context, and safety flags.

### JSON request bodies

Body-based SDK methods accept a JSON file through `--file`; use `--file -` to read JSON from standard input.

```bash
asa campaigns query --file query.json
printf '{"pagination":{"pageSize":100}}' | asa campaigns query --file -
```

The generated references document all 35 request-model schemas, required fields, enums, and nested required-field skeletons. Find the exact entry without exploring the CLI:

```bash
python scripts/lookup_command.py "search term popularity"
python scripts/lookup_command.py --sdk-method campaigns_post
python scripts/lookup_command.py --resource recommendations
```

Start with [the command index](references/command-index.md) for the complete inventory.

### Mutation safety

Create, update, delete, bulk apply/dismiss, and upload commands do not send a request unless `--confirm` is present. Without it, the CLI validates and prints a JSON preview.

```bash
# Validates and previews only
asa campaigns create --file campaign.json

# Sends exactly one SDK mutation after review
asa campaigns create --file campaign.json --confirm

# Explicit validation-only mode
asa campaigns create --file campaign.json --dry-run
```

Read the resource back after a confirmed mutation. A successful request without matching readback is not considered verified.

### Resource families

- Access, ad accounts, apps, and eligibility
- Campaigns, ad groups, ads, creatives, and product pages
- Targeting keywords and negative keywords
- Shared budgets
- Business brands and business categories for Apple Maps
- Geos, locations, location groups, and assets
- App and business-brand reports
- Impression share and search-term popularity insights
- Recommendations and suggestions
- Change-history summaries and details

The asset upload endpoint has an explicit multipart wrapper:

```bash
asa assets upload \
  --file brand.png \
  --promoted-object-id BRAND_ID \
  --promoted-object-type BUSINESS_BRAND

# Add --confirm only after reviewing the preview.
```

## Opinionated workflows

Only behavior that remains useful above the official SDK is being ported into `asa workflows`.

The current v1-backed workflows are:

```bash
# Complete, paginated, read-only campaign-structure audit
asa workflows campaigns audit

# Local four-campaign plan; never sends a mutation
asa workflows campaigns plan-four-structure --daily-budget 25
```

The four-campaign convention remains available as an opt-in planning tool; it is not imposed by raw SDK commands.

Older setup, clone, keyword-promotion, optimization, custom-report, and CPP-experiment behavior remains available only under `asa v5` until each workflow is either ported with equivalent evidence or explicitly retired.

## Legacy v5

Existing v5 behavior is isolated and still callable:

```bash
asa v5 campaigns list
asa v5 campaigns audit
asa v5 keywords promote "winning term" --target category
asa v5 reports summary --days 7
asa v5 optimize --dry-run
```

The import path `asa_cli.api` remains a compatibility re-export of `asa_cli.v5.api`. New code should use the explicit v5 path.

## Codex skill

This repository is also a Codex skill. [SKILL.md](SKILL.md) is a short router backed by deterministic generated references rather than a handwritten command catalog.

Before an SDK or CLI release, verify that the skill and runtime still agree:

```bash
python scripts/generate_skill_references.py --check
python scripts/lookup_command.py --sdk-method impression_share_query
```

## Development and completeness gates

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest -q
uv run python -m asa_cli.platform.generate_manifest --check
uv run python scripts/generate_skill_references.py --check
```

The checked-in manifest records:

- SDK distribution and version
- upstream source commit and release URL
- all 99 public canonical method signatures
- HTTP paths, context mode, scalar/body/multipart parameters, mutation class, and pagination shape
- JSON Schema plus source and schema hashes for 35 request models

CI runs on Python 3.12, 3.13, and 3.14.

## Scope and live verification

The manifest and tests prove SDK and CLI coverage; they do not prove that every endpoint is enabled for every Apple Ads account. Account eligibility, Apple-side rollout state, permissions, and live response behavior must be verified with safe reads in the intended account. Do not use a mutation as an availability probe.

## License

MIT
