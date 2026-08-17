# Reporting and custom product page experiments

## Complete date windows

Report defaults end yesterday and include exactly `--days` completed calendar
dates. `--start` and `--end` are inclusive aliases for `--start-date` and
`--end-date`. An end date of today or later is rejected rather than mixing a
partial day into a comparison. Lower-level v5 report helpers likewise default
to 30 inclusive completed ORTZ dates rather than partial today. The budget
status dashboard prints the exact spend window and coverage it used.

`summary`, `keywords`, `search-terms`, and `ads` support stable JSON. The
versioned v5 envelope is:

```json
{
  "schema_version": 1,
  "report_type": "keywords",
  "window": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-07",
    "days": 7,
    "time_zone": "ORTZ",
    "complete": true
  },
  "inventory_complete": true,
  "rows": [],
  "totals": {},
  "source_totals": {},
  "coverage": {
    "api_pages_complete": true,
    "source_rows": 0,
    "filtered_rows": 0,
    "returned_rows": 0,
    "selection_complete": true,
    "truncated": false,
    "totals_scope": "returned_rows",
    "source_totals_scope": "apple_grand_totals"
  }
}
```

Rates are numeric fractions, money is numeric in the account currency, missing
ratios are `null`, and rows have deterministic order. `totals` remains the sum of
the returned rows for compatibility. Use `source_totals` for comparisons between
campaign, keyword, ad, and search-term reports: it prefers Apple's grand total,
which avoids both display filtering and independent row-level money rounding.
Only treat returned rows as the full selected set when
`coverage.selection_complete` is `true`; `coverage` records every CLI filter,
limit, row count, and verified API page count.

All comparable v5 performance reports use `ORTZ`, Apple's organization-relative
time zone. UTC remains useful for invoice reconciliation, but a UTC campaign
total must not be compared with an ORTZ search-term total for the same date
labels. Search-term reports only support ORTZ and Apple applies a 10-impression
disclosure threshold; low-volume terms can appear as an aggregated `other` row.

For absence-based keyword analysis, use
`reports keywords --all --include-zero --json` and require
`inventory_complete: true`. Performance-only output must not be interpreted as a
complete targeting-keyword inventory.

## Pagination and automation contract

The v5 client follows top-level Apple report pagination until every
`totalResults` row is collected. A full 1,000-row page without response
pagination fails closed because completeness cannot be certified. The custom
report catalog likewise follows all 50-row pages. CLI `--limit` and
`--min-impressions` operate only after the complete API result is fetched and
are reflected in `coverage`; they never silently redefine `source_totals`.

Platform API v1 report and insight commands are exact one-request SDK wrappers.
They intentionally preserve Apple's response shape instead of inventing a
second envelope. Their request pagination defaults to 100 rows and supports up
to 5,000. Automation must continue increasing `pagination.offset` until the
response satisfies `offset + pageSize >= totalCount`; a response page is not a
complete report merely because the command exited successfully.

For Platform API v1 app and business-brand performance reports:

- set the same explicit `timeRange.start`, `timeRange.end`, granularity, and
  `timeRange.timeZone` on every report being compared;
- use `ORTZ` when a search-term report participates, because search terms do not
  support UTC;
- request `options.includeRows: ["GRAND_TOTAL"]` when a comparable aggregate is
  required, and do not substitute a sum of a filtered page;
- exclude today from completed-day comparisons.

Platform API v1 impression-share and search-term-popularity Insights are fixed
to UTC by Apple's model. Their periods and pagination can be compared with each
other, but their date boundaries must not be presented as identical to ORTZ
performance windows without an explicit timezone reconciliation.

`asa v5 optimize` now uses the same exact completed ORTZ window and complete
paginated search-term source. Its JSON includes `window`, `source_totals`, and
`coverage`; its CPA and spend thresholds are explicitly denominated in the
organization currency. Winner and loser lists remain filtered action candidates
rather than account totals.

## Impression share

`reports impression-share` uses Apple's asynchronous `/custom-reports` endpoint,
not ordinary keyword impressions. It downloads and parses Apple's short-lived CSV
as soon as the report completes. Rows contain `low_impression_share`,
`high_impression_share`, `rank`, and `search_popularity` for app, country, search
term, and date. These deciles are first-party observations; they are not estimates
of competitor bids.

Creating reports is rate limited, so `--report-id` can reuse a report. A custom
date window may contain at most 30 days.
With `--no-wait`, a queued or running report returns no rows and explicitly sets
`coverage.report_complete` and `coverage.selection_complete` to `false`; it is
not an empty completed result.

## Existing custom product pages

App Store Connect remains the authoring system for custom product pages. The ASA
CLI only validates an existing Apple Ads creative and attaches it to an ad group.
A manifest is intentionally small:

```json
{
  "schema_version": 1,
  "experiment_id": "focused-long-screenshots",
  "hypothesis": "A focused page improves conversion for long screenshot intent.",
  "adam_id": 123456789,
  "custom_product_page_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "campaign_id": 123,
  "ad_group_id": 456,
  "treatment": {
    "name": "Long screenshot CPP",
    "creative_id": 789,
    "ad_id": null,
    "initial_status": "PAUSED"
  }
}
```

`asa ads experiment manifest.json` is read-only. `--apply` is the explicit
mutation gate and requires immediate matching readback. Once the returned ad ID is
recorded in the manifest, `asa reports ads --campaign 123 --json` supplies the
complete-window exposure, installs, spend, and CPA data. Downstream value and the
continue/stop/gather-more-data decision belong in the caller's private measurement
policy, not this general-purpose CLI.
