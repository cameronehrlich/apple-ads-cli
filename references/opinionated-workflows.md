# Opinionated workflows

These workflows are higher-level operating logic, not direct Platform API endpoint wrappers. Keep them under `asa workflows ...` and reintroduce them selectively when they remain useful on top of v1.

Current classification:

- Retain multi-app configuration, stable JSON contracts, completed-window reporting, dry-run gates, and immediate readback doctrine.
- Ported to v1 workflows: `asa workflows campaigns audit` reads the complete paginated campaign set through the official SDK and emits read-only JSON; `asa workflows campaigns plan-four-structure` is a local dry-run plan and sends no Apple mutation.
- Legacy-only under `asa v5`: four-campaign setup mutation, campaign cloning, keyword promotion/routing, search-term optimization, CPP attachment experiments, and asynchronous v5 custom reports.
- Superseded: v5 impression-share and embedded bid-recommendation commands should yield to raw v1 insights and recommendation endpoints.

These classifications describe local implementation. They do not imply that a command has been accepted by a live Apple account.

## Four-campaign structure

The existing structure separates intent:

| Campaign | Purpose | Match behavior |
|---|---|---|
| Brand | App or company name | Exact; Search Match off |
| Category | Non-branded product intent | Exact; Search Match off |
| Competitor | Competitor names | Exact; Search Match off |
| Discovery | Search-term mining | Broad plus Search Match |

Campaign-name heuristics are convenience, not identity proof. Resolve campaign IDs and current settings before acting.

## Keyword routing and promotion

The existing routing workflow adds exact-match terms to the selected Brand, Category, or Competitor campaign; broad variants to Discovery; and Discovery negatives that reduce overlap. Promotion moves a proven Discovery search term into the appropriate exact campaign and adds the corresponding Discovery negative.

Before retaining this behavior for v1, verify that it still adds value beyond Apple's keyword suggestions and recommendations. Suggestions provide candidate inputs; recommendations are actionable Apple-managed opportunities. Neither automatically replaces account-specific routing, negative-keyword control, or a documented promotion policy.

## Weekly optimization

Use adjacent, inclusive, completed date windows. Pull current campaign, keyword, search-term, budget, recommendation, and impression-share evidence before proposing changes. Treat improved CPA and budget constraint as separate questions.

Default sequence:

1. Read and compare the latest complete window with the immediately preceding window.
2. Identify constrained budgets, proven winners, and spend without installs.
3. Preview the smallest justified bid, keyword, negative, or budget change.
4. Obtain approval for the exact mutation when not already authorized.
5. Apply and immediately read back each changed resource.
6. Record IDs, before/after values, verification, and the next review point.

Do not use an unattended optimization workflow to broaden scope, increase spend, or apply/dismiss Apple recommendations without explicit policy and authorization.

## Derived reporting

Higher-level reports remain useful when they add stable semantics that the SDK does not provide directly:

- Complete configured keyword inventories including zero-activity rows.
- Winners and negative candidates from stated thresholds.
- Budget-health and campaign-structure audits.
- Stable JSON envelopes and deterministic sorting.
- Cross-resource summaries that preserve source IDs and time windows.

Keep thresholds explicit. Do not label a term a winner, loser, or negative candidate without the applied date window and rule.

## Creative and CPP experiments

Validate the manifest and referenced creative first. Preview attachment by default, require an explicit mutation gate, and immediately read back the created ad. Track exposure, installs, spend, and CPA over complete windows; leave continue, stop, and value decisions to an explicit caller policy.

## v5 fallback

Use a legacy workflow only when its generated v5 reference identifies a supported fallback and v1 lacks the required implemented operation. Keep v5 input/output normalization at the compatibility boundary. Never pass raw v5 shapes into new v1 workflow logic.
