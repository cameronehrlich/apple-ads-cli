---
name: apple-search-ads-cli
description: Use the ASA CLI for Apple Ads Platform API v1 and legacy Apple Search Ads API v5. Trigger when Codex needs exact CLI syntax for campaigns, ad groups, ads, creatives, keywords, negatives, budgets, accounts, apps, Apple Maps brands or locations, reports, impression share, search-term popularity, recommendations, suggestions, change history, v5 migration or fallback, or this repository's strategy audit, manual search-results, Maximize Conversions, campaign-structure, and optimization workflows. Also use when mapping an Apple SDK endpoint to its CLI wrapper or safely executing Apple Ads mutations.
---

# Apple Ads CLI

Use this skill to select an exact command from the generated catalog and run it with the required context and safety checks. Do not reconstruct command syntax from memory or probe live Apple endpoints to discover inputs.

## Start here

Work from the repository root. If `uv` is not on `PATH` in Cameron's environment, use `/Users/cameronehrlich/.local/bin/uv`.

1. Find the operation before loading detailed documentation:

   ```bash
   uv run python scripts/lookup_command.py "search term popularity"
   uv run python scripts/lookup_command.py --sdk-method search_term_popularity_query
   uv run python scripts/lookup_command.py --resource recommendations
   uv run python scripts/lookup_command.py --version v5 --command "asa v5 reports custom"
   ```

2. Read the complete reference named by the lookup result.
3. Read [configuration-and-context.md](references/configuration-and-context.md) when credentials, account scope, App Store versus Maps surface, or request bodies matter.
4. Read [safety-and-output-contracts.md](references/safety-and-output-contracts.md) before any mutation, unattended operation, report comparison, or machine-readable integration.
5. Execute only commands whose generated entry says `implemented`. Treat `inventory-only`, `planned`, `blocked`, and `unverified` as documentation, not runnable proof.

## Choose the command surface

- Prefer `asa <resource> <action>` for Platform API v1 endpoint wrappers.
- Use `asa v5 ...` only when the user explicitly requests v5 or the required v1 operation is not implemented and the generated migration reference identifies a supported fallback.
- Use `asa workflows ...` for higher-level local logic. Read [opinionated-workflows.md](references/opinionated-workflows.md) and the generated [workflow-command-index.md](references/workflow-command-index.md) first.
- Do not count workflows or v5 compatibility commands as v1 SDK endpoint coverage.

## Select a strategy workflow

- Use `asa workflows campaigns audit --strategy auto` for read-only strategy classification and applicable checks. It distinguishes `manual-search-results`, `maximize-conversions`, and `non-search-or-unsupported` from API evidence and skips cross-strategy failures.
- Use `asa workflows campaigns plan-four-structure` only for manual App Store search-results themes. Brand, Category, Competitor, and Discovery may be separate campaigns or themed ad groups; they are not universal requirements.
- Use `asa workflows campaigns plan-maximize-conversions` for a no-write target-CPA plan with eligibility, source/confidence, approximate five-conversions-per-day budget capacity, Search Match automation, and the two-week learning guard.
- Treat Search tab, Today tab, product pages, and Apple Maps as placement-specific. Read [placement-strategy-decision.md](references/placement-strategy-decision.md); do not route them through either search-results planner.

Temporary preview namespaces do not redefine the canonical interface. If an entry documents both a preview path and an eventual canonical path, use only the path marked implemented by the manifest.

## Route to the smallest reference

Read [command-index.md](references/command-index.md) only for broad inventory questions. For a concrete task, load one generated domain reference:

- Accounts, organizations, advertiser resources, ACLs: [v1-accounts-and-access.md](references/v1-accounts-and-access.md)
- Campaigns: [v1-campaigns.md](references/v1-campaigns.md)
- Ad groups: [v1-ad-groups.md](references/v1-ad-groups.md)
- Ads and creatives: [v1-ads-and-creatives.md](references/v1-ads-and-creatives.md)
- Targeting keywords: [v1-keywords.md](references/v1-keywords.md)
- Negative keywords: [v1-negative-keywords.md](references/v1-negative-keywords.md)
- Shared budgets: [v1-shared-budgets.md](references/v1-shared-budgets.md)
- Apps, product pages, eligibility, rejection reasons: [v1-apps-and-product-pages.md](references/v1-apps-and-product-pages.md)
- Maps brands and categories: [v1-maps-brands-and-categories.md](references/v1-maps-brands-and-categories.md)
- Maps locations, location groups, and geo: [v1-maps-locations-and-geo.md](references/v1-maps-locations-and-geo.md)
- Assets: [v1-assets.md](references/v1-assets.md)
- App and Maps reports: [v1-reports.md](references/v1-reports.md)
- Impression share and search-term popularity: [v1-insights.md](references/v1-insights.md)
- Recommendations and suggestions: [v1-recommendations-and-suggestions.md](references/v1-recommendations-and-suggestions.md)
- Audit summaries and change details: [v1-change-history.md](references/v1-change-history.md)
- Any newly introduced family awaiting explicit routing: [v1-other.md](references/v1-other.md)
- Legacy fallback: [v5-fallback.md](references/v5-fallback.md)
- Endpoint migration: [migration-map.md](references/migration-map.md)

## Execute safely

- Begin with read-only preflight and exact account selection.
- Show the user the exact targets and proposed values before a mutation unless that exact action was already authorized.
- Use the command's documented preview or confirmation gate. Never invent `--apply`, `--yes`, or other flags.
- After a mutation, read back the affected resource by ID and compare the intended fields. A successful request without matching readback is unverified.
- Do not automatically retry an ambiguous mutation failure.
- Keep credentials, private keys, client secrets, access tokens, and signed payloads out of output and logs.

## Check catalog freshness

The generated references are release-pinned and reconciled to the public v1, v5, and workflow Typer trees. Before claiming complete coverage after any SDK or command registration update, run:

```bash
uv run python scripts/generate_skill_references.py --check
```

If the installed SDK, manifest provenance, generated references, and runtime command registration disagree, stop and report the mismatch. Do not guess or test against the live API.
