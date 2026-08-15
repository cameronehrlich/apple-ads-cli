# Multi-placement planning decision

Decision: **retain as documentation and defer a combined planner** for 1.1.0.

A single command would imply that the same objective, inputs, controls, and health checks apply across placements. They do not. The Platform API v1 endpoint wrappers remain available for callers that already have a placement-specific plan, while the opinionated workflow surface stays bounded to contracts the CLI can explain and test.

This is a read-only design decision. No campaign, bid, budget, creative, or spend was changed while preparing it.

## Placement matrix

| Placement | Primary planning inputs | Bid and targeting differences | Creative and measurement | 1.1.0 workflow treatment |
|---|---|---|---|---|
| App Store search results, manual CPT | Countries or regions, keyword themes, match type, Search Match, negative overlap, daily budget | Manual CPT with exact or broad keywords and optional Search Match | Default or custom product page ad; tap-through reporting | `plan-four-structure` and the manual mode of `audit` apply |
| App Store search results, Maximize Conversions | Eligible app, countries or regions, target CPA, daily budget, campaign age | Automated bidding and Search Match; separate discovery groups and manual keyword bids are not required | Conversion learning and recommendation evidence; avoid premature changes | `plan-maximize-conversions` and the Maximize Conversions mode of `audit` apply |
| Search tab | App and countries or regions | No keyword list; placement-level bid and audience controls differ from search results | Promotes discovery before a search; evaluate view-through and total metrics as well as taps | No opinionated planner; use exact v1 endpoints with placement-specific owner policy |
| Today tab | App, countries or regions, approved Today tab creative | No search-term intent contract | Custom creative and broader discovery context; evaluate view-through and total metrics | No opinionated planner; creative approval and attribution policy are unresolved inputs |
| Product pages | App, countries or regions, product-page placement and creative choice | No search-results keyword-theme contract | Reaches users while browsing app pages; evaluate view-through and total metrics | No opinionated planner; use exact v1 endpoints with a placement-specific experiment plan |
| Apple Maps | Business brand, locations or location groups, geos, assets, business-category context | Separate MAPS supply source and business-resource model | Location and brand assets; Maps reports are separate from app reports | Explicitly outside App Store search-results planners; use Maps resource commands |

First-party basis:

- Apple’s [ad placements guidance](https://ads.apple.com/app-store/best-practices/ad-placements) distinguishes the placement objectives, creative, and view-through/total measurement considerations.
- Apple’s [campaign structure guidance](https://ads.apple.com/app-store/help/campaigns/0056-structure-campaigns) scopes Brand, Category, Competitor, and Discovery themes to search-results organization and allows structure to reflect country, budget, and objective needs.
- Apple’s [Maximize Conversions guidance](https://ads.apple.com/app-store/best-practices/maximize-conversions) describes automated bidding, Search Match, target CPA, budget capacity, and a learning period that differ from manual keyword structure.
- The pinned official `apple-ads-platform==1.109.0` manifest exposes MAPS through business-brand, location, asset, geo, and reporting resources rather than the App Store campaign workflow contract.

## Why a combined command is deferred

The CLI does not yet have a single first-party model that can validate all of the following before planning: placement eligibility, creative approval and constraints, cross-placement attribution, comparable view-through windows, owner objectives, and placement-specific bid semantics. Filling those gaps with defaults would create unsupported recommendations.

A future command should be proposed only with a bounded contract such as:

```text
asa workflows placements plan --placement PLACEMENT --objective OBJECTIVE ...
```

Its tests would need one fixture per placement, explicit unsupported-input failures, creative/eligibility preflight, attribution provenance, deterministic no-write JSON, and a proof that no search-results keyword check is applied to non-search inventory. That future implementation should be a separate owner-reviewed feature and mutation authorization must remain separate.
