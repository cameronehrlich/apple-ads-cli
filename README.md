# Apple Ads CLI

An independent, scriptable command-line interface for Apple Ads. It wraps every public operation in Apple’s official Python SDK, preserves the previous Campaign Management API v5 implementation, and adds safety-focused workflows for real advertising accounts.

The project follows Apple’s current Apple Ads name. The established `asa` executable, `asa-cli` Python distribution, and `asa_cli` import package remain unchanged for compatibility. The bundled Codex skill is invoked as `$apple-ads-cli`.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apple Ads Platform SDK 1.109.0](https://img.shields.io/badge/Apple%20Ads%20Platform%20SDK-1.109.0-black.svg)](https://github.com/apple/apple-ads-platform-api-python/releases/tag/v1.109.0)
[![CI](https://github.com/cameronehrlich/apple-ads-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/cameronehrlich/apple-ads-cli/actions/workflows/ci.yml)

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
git clone https://github.com/cameronehrlich/apple-ads-cli.git
cd apple-ads-cli

uv sync --all-extras
uv run asa version
uv run asa --help
```

An editable pip install also works:

```bash
python3.12 -m pip install -e '.[dev]'
asa version
```

Automation should install the exact 1.1.2 tag rather than following `main`:

```bash
uv tool install 'git+https://github.com/cameronehrlich/apple-ads-cli.git@1.1.2'
```

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
Platform API report and insight commands return exactly one requested Apple page;
automation must inspect `pagination` and advance `offset` through `totalCount`.

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

The preview includes the resolved context and exact ad-account ID. A conflicting
`adAccountId` in the request body fails before SDK invocation. Mutation request
bodies require `--file`. Omitted request fields stay omitted on the preview and
wire; treat any explicit null that appears in the preview as intentional. For
App Store search-results campaign creation, pair `supplySource: APPSTORE` with
`supplyPlacement: APPSTORE_SEARCH_RESULTS`; `SEARCH_RESULTS` is not a valid
create value. Ad-group creation requires `startTime`. Asset uploads require an
existing, readable PNG, JPEG, or HEIC file.

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

## Optional higher-level workflows

Only behavior that remains useful above the official SDK is ported into `asa workflows`.

```bash
# Complete, paginated, read-only strategy audit
asa workflows campaigns audit --strategy auto --ad-account AD_ACCOUNT_ID

# Manual App Store search-results themes; never sends a request
asa workflows campaigns plan-four-structure \
  --grouping themed-ad-groups \
  --daily-budget 100

# Maximize Conversions plan; optional Apple reads, never a mutation
asa workflows campaigns plan-maximize-conversions \
  --adam-id APP_ADAM_ID \
  --countries US,GB \
  --target-cpa 12 \
  --daily-budget 60
```

The audit detects `manual-search-results`, `maximize-conversions`, or `non-search-or-unsupported` from placement, supply-source, and bid-strategy evidence before considering campaign names. It never applies one strategy's health failures to another strategy. Optional `--strategy manual|maximize-conversions` overrides fail closed when they conflict with reliable API evidence.

Brand, Category, Competitor, and Discovery are manual search-results themes, not a universal account requirement. The manual planner supports separate campaigns or themed ad groups, keeps every budget unapproved, and documents exact-match, Search Match, and negative-overlap intent. The Maximize Conversions planner instead preserves target-CPA provenance, eligibility, an approximate five-conversions-per-day budget-capacity check, and a two-week learning guard. Both emit `dryRun=true` and `mutationAvailable=false`.

Search tab, Today tab, product pages, and Apple Maps require placement-specific plans. They are intentionally outside these search-results planners; see the [multi-placement decision](references/placement-strategy-decision.md).

Four-campaign setup, cloning, keyword promotion/routing, search-term optimization, custom reports, and CPP experiments remain available under `asa v5` until deliberately ported or retired.

```bash
asa v5 campaigns audit
asa v5 keywords promote 'winning term' --target category
asa v5 reports custom --days 30
asa v5 optimize --dry-run
```

Comparable v5 performance reports use completed `ORTZ` date windows and fetch
every Apple page. Stable JSON keeps returned-row `totals` for compatibility and
adds `source_totals` plus explicit filter/limit/page `coverage`. See the
[reporting and automation contract](docs/REPORTING-AND-CPP.md) before comparing
campaign, keyword, ad, search-term, or fixed-UTC Insights data.

The Python import path `asa_cli.api` remains a compatibility re-export of `asa_cli.v5.api`. New compatibility code should import `asa_cli.v5.api` explicitly.

## Codex skill and command discovery

This repository is also a Codex skill. [SKILL.md](SKILL.md) is a compact router backed by generated, release-pinned references.

```bash
python scripts/lookup_command.py 'search term popularity'
python scripts/lookup_command.py --sdk-method impression_share_query
python scripts/lookup_command.py --resource recommendations
python scripts/lookup_command.py 'audit campaign strategy'
python scripts/lookup_command.py 'manual search results plan'
python scripts/lookup_command.py 'maximize conversions plan'
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

The checked-in manifest records the SDK version and source commit, all 99 method
signatures, HTTP paths, context modes, parameter classifications, mutation and
pagination metadata, and JSON Schemas with hashes for 35 request models. It also
maps every operation to one of 71 root response models and audits all 220 models
reachable through those responses, including strict fields, identifiers, enums,
and custom validators.

### Live response drift

Apple's live service can occasionally disagree with the generated SDK model.
The CLI always attempts official SDK deserialization first. A raw JSON response
is preserved only for a small, tested set of live-confirmed mismatches. Before
that fallback is accepted, a patched copy is run through the SDK again so a
known first error cannot hide a later unrelated type or enum failure. The
original wire values remain unchanged in CLI output.

When updating the SDK, review both request- and response-model manifest diffs.
Do not broaden compatibility based on a plausible example alone: capture a
sanitized live failure, match its response type and exact field/type condition,
add near-miss tests, and retain fail-closed behavior for everything else.
See the [SDK response-drift audit](references/sdk-response-drift-audit.md) for
the current inventory, confirmed exceptions, and deliberately unhandled risks.

See [CONTRIBUTING.md](CONTRIBUTING.md) for endpoint and regression-test guidance.

## Releases and compatibility

The CLI uses semantic versions and bare tags such as `1.1.0`. GitHub Releases contain the wheel, source distribution, generated release notes, and SHA-256 checksums.

| Release | Public contract |
|---|---|
| `1.0.0` | Immutable legacy Campaign Management API v5 baseline from the former `main` code line |
| `1.1.0` | Backward-compatible Platform API v1 default, explicit `asa v5` fallback, generated skill, and strategy-aware workflows |
| `1.1.1` | Response-model drift inventory and fail-closed validation hardening for confirmed live SDK mismatches |
| `1.1.2` | Apple Ads CLI repository branding and organization-currency-safe legacy v5 campaign, ad group, keyword, and budget writes |

CLI and SDK versions are intentionally independent:

- `asa 1.1.2` describes this project’s command and behavior contract.
- `apple-ads-platform 1.109.0` identifies the exact Apple SDK contract it wraps.

Automation should pin a CLI release, run `asa config test`, and perform a safe read before depending on an endpoint. See [RELEASING.md](RELEASING.md) for the release process and versioning policy.

## Project status

The project is beta software operating against advertising accounts. Local tests and manifest reconciliation do not prove account eligibility, Apple-side rollout state, permissions, or live response behavior. Verify availability with safe reads; never use a mutation as an endpoint probe.

This project is independent and unofficial. It is not affiliated with, endorsed by, or sponsored by Apple Inc. Apple Ads, App Store, and Apple are trademarks of Apple Inc.

## License

MIT
