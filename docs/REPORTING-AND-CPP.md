# Reporting and custom product page experiments

## Complete date windows

Report defaults end yesterday and include exactly `--days` completed calendar
dates. `--start` and `--end` are inclusive aliases for `--start-date` and
`--end-date`. An end date of today or later is rejected rather than mixing a
partial day into a comparison.

`summary`, `keywords`, `search-terms`, and `ads` support stable JSON. The v1
envelope is:

```json
{
  "schema_version": 1,
  "report_type": "keywords",
  "window": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-07",
    "days": 7,
    "time_zone": "UTC",
    "complete": true
  },
  "inventory_complete": true,
  "rows": [],
  "totals": {}
}
```

Rates are numeric fractions, money is numeric in the account currency, missing
ratios are `null`, and rows have deterministic order. For absence-based keyword
analysis, use `reports keywords --all --include-zero --json` and require
`inventory_complete: true`. Performance-only output must not be interpreted as a
complete targeting-keyword inventory.

## Impression share

`reports impression-share` uses Apple's asynchronous `/custom-reports` endpoint,
not ordinary keyword impressions. It downloads and parses Apple's short-lived CSV
as soon as the report completes. Rows contain `low_impression_share`,
`high_impression_share`, `rank`, and `search_popularity` for app, country, search
term, and date. These deciles are first-party observations; they are not estimates
of competitor bids.

Creating reports is rate limited, so `--report-id` can reuse a report. A custom
date window may contain at most 30 days.

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
