<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Workflow command inventory

This namespace contains 2 public command leaves. Workflows are higher-level local logic, not one-to-one SDK endpoint coverage.

## Contents

- `asa workflows campaigns audit`
- `asa workflows campaigns plan-four-structure`

## `asa workflows campaigns audit`

Read and audit the complete campaign set without changing live state.

- Usage: `Usage: asa workflows campaigns audit [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--page-size` | no | `integer range` | `100` | — | Campaigns per SDK query |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa workflows campaigns plan-four-structure`

Print a no-write four-campaign plan for owner review.

- Usage: `Usage: asa workflows campaigns plan-four-structure [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--countries` | no | `text` | — | — | Comma-separated country or region codes; defaults to configured app countries |
| option | `--daily-budget` | no | `float range` | — | — | Planning value per campaign; no API mutation is sent |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
