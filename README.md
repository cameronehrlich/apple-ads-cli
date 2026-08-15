# Apple Ads CLI

An independent, scriptable command-line interface for Apple Ads. It wraps every public operation in Apple’s official Python SDK, preserves the previous Campaign Management API v5 implementation, and adds safety-focused workflows for real advertising accounts.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apple Ads Platform SDK 1.109.0](https://img.shields.io/badge/Apple%20Ads%20Platform%20SDK-1.109.0-black.svg)](https://github.com/apple/apple-ads-platform-api-python/releases/tag/v1.109.0)
[![CI](https://github.com/cameronehrlich/apple-search-ads-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/cameronehrlich/apple-search-ads-cli/actions/workflows/ci.yml)

## Why this CLI

- **Complete SDK coverage:** all 99 canonical methods in `apple-ads-platform==1.109.0`, organized into 24 explicit resource families.
- **New Apple insights:** impression share, search-term popularity, country/region reporting, recommendations, and suggestions.
- **Safe account operations:** mutations preview by default, require `--confirm`, expose the resolved ad-account context, and reject account mismatches before sending.
- **A deliberate migration path:** the official Platform API is the default; proven higher-level behavior lives under `workflows`; the previous implementation remains under `v5`.
- **Agent-ready documentation:** the repository includes a generated Codex skill with exact commands, options, request schemas, and safety rules.

Coverage is checked mechanically against a pinned SDK manifest. That proves local CLI completeness, not that Apple has enabled every endpoint for every account.

## Quick start

Python 3.12 or newer and [uv](https://docs.astral.sh/uv/) are required for the recommended development install.

```bash
git clone https://github.com/cameronehrlich/apple-search-ads-cli.git
cd apple-search-ads-cli

uv sync --all-extras
uv run asa version
uv run asa --help
```

An editable pip install also works:

```bash
python3.12 -m pip install -e '.[dev]'
asa version
```

Once versioned releases begin, automation should install an exact tag rather than following `main`:

```bash
uv tool install 'git+https://github.com/cameronehrlich/apple-search-ads-cli.git@1.0.0'
```

Do not use that example until the corresponding GitHub release exists.

## Configure

```bash
asa config setup
asa config show
asa config test
```

Credentials use Apple’s client ID, team ID, key ID, and EC private key. The saved credentials file uses mode `0600`; private keys and credential files are ignored by Git.

Most ad-serving resources also require an Apple Ads Platform ad-account context. Supply it, in precedence order, through:

1. `--ad-account AD_ACCOUNT_ID`
2. `ASA_AD_ACCOUNT_ID`
3. `ad_account_id` saved by `asa config setup`

The legacy v5 organization ID is intentionally never treated as the Platform API ad-account ID.

## Command architecture

| Surface | Contract | Example |
|---|---|---|
| `asa <resource> <action>` | Exact wrappers around the official Platform SDK | `asa campaigns query --file query.json` |
| `asa workflows ...` | Selected higher-level behavior above the SDK | `asa workflows campaigns audit` |
| `asa v5 ...` | Frozen compatibility surface for the prior CLI | `asa v5 reports summary --days 7` |

Use concrete help as the runtime source of truth:

```bash
asa campaigns --help
asa campaigns query --help
asa insights search-term-popularity --help
```

### Official Platform API examples

```bash
asa campaigns get --id CAMPAIGN_ID
asa campaigns query --file query.json
asa ad-groups query --file query.json
asa keywords bulk-create --file keywords.json
asa negative-keywords query --file query.json

asa insights impression-share --file impression-share.json
asa insights search-term-popularity --file popularity.json

asa recommendations daily-budget-query --file recommendations.json
asa recommendations target-cpa-query --file recommendations.json
asa suggestions keywords --file suggestions.json

asa reports-apps campaign --file report.json
asa reports-apps search-term --file report.json
```

Body-based methods accept JSON through `--file`; use `--file -` for standard input.

```bash
printf '{"pagination":{"pageSize":100}}' \
  | asa campaigns query --file -
```

### Impression share

Impression share measures bounded paid visibility for an app, search term, and country/region. It is not organic rank, exact search volume, competitor bid data, or share of installs. Apple supports first-slot and all-slot views.

```json
{
  "filters": [
    {
      "field": "promotedObjectId",
      "operator": "EQUALS",
      "value": "123456789"
    }
  ],
  "options": {
    "impressionShareReportType": "ALL_SLOTS"
  },
  "timeRange": {
    "start": "2026-08-02",
    "end": "2026-08-08",
    "granularity": "WEEKLY_SUN_SAT"
  }
}
```

```bash
asa insights impression-share \
  --file impression-share.json \
  --ad-account AD_ACCOUNT_ID
```

### Search-term popularity

Search-term popularity is market-level relative demand by country/region and App Store genre. It is not the promoted app’s traffic or an exact query count. Weekly data has rolling 65-week retention; monthly data has rolling 15-month retention.

```json
{
  "timeRange": {
    "start": "2026-08-02",
    "end": "2026-08-08",
    "granularity": "WEEKLY_SUN_SAT"
  },
  "pagination": {
    "offset": 0,
    "pageSize": 5000
  }
}
```

```bash
asa insights search-term-popularity \
  --file popularity.json \
  --ad-account AD_ACCOUNT_ID
```

Keep the returned country/region, genre, and period attached to every interpretation.

## Mutation safety

Create, update, delete, upload, and recommendation apply/dismiss commands validate and print a JSON preview unless `--confirm` is present.

```bash
# Preview only
asa campaigns create --file campaign.json

# Explicit validation-only mode
asa campaigns create --file campaign.json --dry-run

# Sends one mutation after review
asa campaigns create --file campaign.json --confirm
```

The preview includes the resolved context and exact ad-account ID. A conflicting `adAccountId` in the request body fails before SDK invocation. Asset uploads require an existing, readable PNG, JPEG, or HEIC file.

After every confirmed mutation, read the resource back and compare each intended field. A successful request without matching readback is unverified.

## Resource families

- Access, ad accounts, apps, and eligibility
- Campaigns, ad groups, ads, creatives, and product pages
- Keywords and negative keywords
- Shared budgets
- Business brands, business categories, geos, locations, and location groups
- Assets and creative rejection reasons
- App and business-brand reports
- Impression share and search-term popularity insights
- Daily-budget and target-CPA recommendations
- Category, keyword, phrase, and target-CPA suggestions
- Change-history summaries and details

The complete inventory and all 35 request-model schemas are in the [generated command index](references/command-index.md).

## Opinionated workflows

Only behavior that remains useful above the official SDK is ported into `asa workflows`.

```bash
# Complete, paginated, read-only structure audit
asa workflows campaigns audit --ad-account AD_ACCOUNT_ID

# Local four-campaign plan; never sends a request
asa workflows campaigns plan-four-structure --daily-budget 25
```

Four-campaign setup, cloning, keyword promotion/routing, search-term optimization, custom reports, and CPP experiments remain available under `asa v5` until deliberately ported or retired.

```bash
asa v5 campaigns audit
asa v5 keywords promote 'winning term' --target category
asa v5 reports custom --days 30
asa v5 optimize --dry-run
```

The Python import path `asa_cli.api` remains a compatibility re-export of `asa_cli.v5.api`. New compatibility code should import `asa_cli.v5.api` explicitly.

## Codex skill and command discovery

This repository is also a Codex skill. [SKILL.md](SKILL.md) is a compact router backed by generated, release-pinned references.

```bash
python scripts/lookup_command.py 'search term popularity'
python scripts/lookup_command.py --sdk-method impression_share_query
python scripts/lookup_command.py --resource recommendations
```

Generated references cover every v1, v5, and workflow command with exact flags, request shapes, and mutation gates. Do not edit them by hand.

## Development

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest -q
uv run python -m asa_cli.platform.generate_manifest --check
uv run python scripts/generate_skill_references.py --check
uv run python scripts/check_release.py
uv build
```

The checked-in manifest records the SDK version and source commit, all 99 method signatures, HTTP paths, context modes, parameter classifications, mutation and pagination metadata, and JSON Schemas with hashes for 35 request models.

See [CONTRIBUTING.md](CONTRIBUTING.md) for endpoint and regression-test guidance.

## Releases and compatibility

The CLI uses semantic versions and bare tags such as `1.0.0`. GitHub Releases will contain the wheel, source distribution, generated release notes, and SHA-256 checksums.

CLI and SDK versions are intentionally independent:

- `asa 1.1.0` describes this project’s command and behavior contract.
- `apple-ads-platform 1.109.0` identifies the exact Apple SDK contract it wraps.

Automation should pin a CLI release, run `asa config test`, and perform a safe read before depending on an endpoint. See [RELEASING.md](RELEASING.md) for the release process and versioning policy.

## Project status

The project is beta software operating against advertising accounts. Local tests and manifest reconciliation do not prove account eligibility, Apple-side rollout state, permissions, or live response behavior. Verify availability with safe reads; never use a mutation as an endpoint probe.

This project is independent and unofficial. It is not affiliated with, endorsed by, or sponsored by Apple Inc. Apple Ads, App Store, and Apple are trademarks of Apple Inc.

## License

MIT
