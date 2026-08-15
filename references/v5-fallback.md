<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Legacy v5 command inventory

This frozen namespace contains 65 public command leaves. The inventory proves local registration only; it does not prove live API acceptance.

## Contents

- `asa v5 acl countries`
- `asa v5 acl eligibility`
- `asa v5 acl list`
- `asa v5 acl me`
- `asa v5 acl search-apps`
- `asa v5 adgroups create`
- `asa v5 adgroups delete`
- `asa v5 adgroups enable`
- `asa v5 adgroups list`
- `asa v5 adgroups pause`
- `asa v5 adgroups update`
- `asa v5 ads create`
- `asa v5 ads creatives`
- `asa v5 ads delete`
- `asa v5 ads experiment`
- `asa v5 ads list`
- `asa v5 ads product-pages`
- `asa v5 ads rejections`
- `asa v5 budget create`
- `asa v5 budget get`
- `asa v5 budget list`
- `asa v5 budget status`
- `asa v5 campaigns audit`
- `asa v5 campaigns clone`
- `asa v5 campaigns create`
- `asa v5 campaigns delete`
- `asa v5 campaigns enable`
- `asa v5 campaigns list`
- `asa v5 campaigns pause`
- `asa v5 campaigns setup`
- `asa v5 campaigns update`
- `asa v5 config add-app`
- `asa v5 config list-apps`
- `asa v5 config remove-app`
- `asa v5 config setup`
- `asa v5 config show`
- `asa v5 config switch`
- `asa v5 config test`
- `asa v5 geo search`
- `asa v5 geo set`
- `asa v5 geo show`
- `asa v5 keywords add`
- `asa v5 keywords add-negatives`
- `asa v5 keywords delete`
- `asa v5 keywords delete-negatives`
- `asa v5 keywords enable`
- `asa v5 keywords find`
- `asa v5 keywords list`
- `asa v5 keywords list-negatives`
- `asa v5 keywords pause`
- `asa v5 keywords promote`
- `asa v5 keywords research`
- `asa v5 keywords update-bid`
- `asa v5 keywords update-bids-bulk`
- `asa v5 optimize`
- `asa v5 reports adgroups`
- `asa v5 reports ads`
- `asa v5 reports bid-recommendations`
- `asa v5 reports custom`
- `asa v5 reports custom-get`
- `asa v5 reports custom-list`
- `asa v5 reports impression-share`
- `asa v5 reports keywords`
- `asa v5 reports search-terms`
- `asa v5 reports summary`

## `asa v5 acl countries`

Show supported countries/regions for advertising.

- Usage: `Usage: asa v5 acl countries [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--filter`, `-f` | no | `text` | — | — | Comma-separated country codes to filter |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 acl eligibility`

Check app advertising eligibility.

- Usage: `Usage: asa v5 acl eligibility [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--app-id`, `-a` | no | `integer` | — | — | Apple App ID (defaults to active app) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 acl list`

Show organizations and roles for the current user.

- Usage: `Usage: asa v5 acl list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 acl me`

Show current user info.

- Usage: `Usage: asa v5 acl me [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 acl search-apps`

Search for iOS apps on the App Store.

- Usage: `Usage: asa v5 acl search-apps [OPTIONS] QUERY`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `QUERY` | yes | `text` | — | — |  |
| option | `--owned`, `--all` | no | `boolean` | `True` | — | Show only owned apps or all |
| option | `--limit`, `-l` | no | `integer` | `20` | — | Maximum results |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups create`

Create a new ad group in a campaign.

- Usage: `Usage: asa v5 adgroups create [OPTIONS] NAME`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| argument | `NAME` | yes | `text` | — | — |  |
| option | `--bid`, `-b` | no | `float` | `1.5` | — | Default bid amount (USD) |
| option | `--search-match`, `--no-search-match` | no | `boolean` | `False` | — | Enable Search Match |
| option | `--status`, `-s` | no | `text` | `ENABLED` | — | Initial status (ENABLED or PAUSED) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups delete`

Delete an ad group. WARNING: This is irreversible.

- Usage: `Usage: asa v5 adgroups delete [OPTIONS] ADGROUP_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `ADGROUP_ID` | yes | `integer` | — | — |  |
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups enable`

Enable an ad group.

- Usage: `Usage: asa v5 adgroups enable [OPTIONS] ADGROUP_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `ADGROUP_ID` | yes | `integer` | — | — |  |
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups list`

List all ad groups for a campaign.

- Usage: `Usage: asa v5 adgroups list [OPTIONS] CAMPAIGN_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `CAMPAIGN_ID` | yes | `integer` | — | — |  |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups pause`

Pause an ad group.

- Usage: `Usage: asa v5 adgroups pause [OPTIONS] ADGROUP_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `ADGROUP_ID` | yes | `integer` | — | — |  |
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 adgroups update`

Update an ad group's settings.

- Usage: `Usage: asa v5 adgroups update [OPTIONS] ADGROUP_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `ADGROUP_ID` | yes | `integer` | — | — |  |
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--name`, `-n` | no | `text` | — | — | New name |
| option | `--bid`, `-b` | no | `float` | — | — | New default bid (USD) |
| option | `--search-match`, `--no-search-match` | no | `boolean` | — | — | Toggle Search Match |
| option | `--status`, `-s` | no | `text` | — | — | New status (ENABLED or PAUSED) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads create`

Create an ad and require immediate readback of its attachment.

- Usage: `Usage: asa v5 ads create [OPTIONS] NAME`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--adgroup`, `-g` | yes | `integer` | — | — | Ad group ID |
| option | `--creative` | yes | `integer` | — | — | Creative ID |
| argument | `NAME` | yes | `text` | — | — |  |
| option | `--status`, `-s` | no | `text` | `ENABLED` | — | Initial status (ENABLED or PAUSED) |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and show the attachment only |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads creatives`

List creatives or get details for a specific creative.

- Usage: `Usage: asa v5 ads creatives [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | no | `integer` | — | — | Get a specific creative by ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads delete`

Delete an ad. WARNING: This is irreversible.

- Usage: `Usage: asa v5 ads delete [OPTIONS] AD_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `AD_ID` | yes | `integer` | — | — |  |
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--adgroup`, `-g` | yes | `integer` | — | — | Ad group ID |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads experiment`

Validate or attach an existing ASC custom product page creative.

App Store Connect authoring remains outside this command. Without
``--apply`` this command performs read-only validation only.

- Usage: `Usage: asa v5 ads experiment [OPTIONS] MANIFEST_PATH`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `MANIFEST_PATH` | yes | `path` | — | — |  |
| option | `--apply` | no | `boolean` | `False` | — | Create the treatment ad; default is read-only dry run |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads list`

List all ads. Provide campaign + ad group for a specific group, or search across all.

- Usage: `Usage: asa v5 ads list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--adgroup`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads product-pages`

List custom product pages for an app.

- Usage: `Usage: asa v5 ads product-pages [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--adam-id`, `-a` | no | `integer` | — | — | App Adam ID (uses current app if not set) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 ads rejections`

Show product page rejection reasons.

- Usage: `Usage: asa v5 ads rejections [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 budget create`

Create a new budget order.

- Usage: `Usage: asa v5 budget create [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--name`, `-n` | yes | `text` | — | — | Budget order name |
| option | `--budget`, `-b` | yes | `float` | — | — | Budget amount (USD) |
| option | `--start`, `-s` | yes | `text` | — | — | Start date (YYYY-MM-DD) |
| option | `--end`, `-e` | yes | `text` | — | — | End date (YYYY-MM-DD) |
| option | `--client-name` | no | `text` | — | — | Client name |
| option | `--email` | no | `text` | — | — | Primary buyer email |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 budget get`

Show details of a specific budget order.

- Usage: `Usage: asa v5 budget get [OPTIONS] BUDGET_ORDER_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `BUDGET_ORDER_ID` | yes | `integer` | — | — |  |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 budget list`

List all budget orders.

- Usage: `Usage: asa v5 budget list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 budget status`

Campaign budget health dashboard.

- Usage: `Usage: asa v5 budget status [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns audit`

Audit current campaign structure against Apple's recommendations.

- Usage: `Usage: asa v5 campaigns audit [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--verbose`, `-v` | no | `boolean` | `False` | — | Show detailed information |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns clone`

Duplicate a campaign (with ad groups, keywords, and negatives).

Apple Ads Campaign Management API v5 has no native campaign-duplication endpoint, so
this reads the source and re-creates it. Useful to escape a stuck
TOTAL_BUDGET_EXHAUSTED state after clearing a lifetime budget —
Apple caches that flag even after the cap is gone, and only a fresh
campaign ID releases it.

The clone preserves: daily budget, countries, supply/channel,
billing event, ad-group structure (name, default bid, pricing
model, targeting dimensions), ACTIVE keywords + bids, and
campaign-level negatives.

Keywords that are PAUSED on the source are NOT copied (usually
intentional). Ad-group-level negatives are NOT copied in this pass
(campaign-level negatives are).

- Usage: `Usage: asa v5 campaigns clone [OPTIONS] SOURCE_CAMPAIGN_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `SOURCE_CAMPAIGN_ID` | yes | `integer` | — | — |  |
| option | `--name`, `-n` | no | `text` | — | — | Name for the clone (defaults to '<source> v2') |
| option | `--keep-lifetime` | no | `boolean` | `False` | — | Copy the source's lifetime budget too. Default: drop it, since Apple is discontinuing lifetime budgets on 2026-06-16 and the most common reason to clone is to escape a stuck TOTAL_BUDGET_EXHAUSTED state. |
| option | `--pause-source` | no | `boolean` | `False` | — | Pause the source campaign after a successful clone. |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns create`

Create a new campaign with custom settings.

- Usage: `Usage: asa v5 campaigns create [OPTIONS] NAME`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `NAME` | yes | `text` | — | — |  |
| option | `--budget`, `-b` | no | `float` | `50.0` | — | Daily budget (USD) |
| option | `--countries`, `-c` | no | `text` | `US` | — | Comma-separated country codes |
| option | `--status`, `-s` | no | `text` | `ENABLED` | — | Initial status (ENABLED or PAUSED) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns delete`

Delete a campaign. WARNING: This is irreversible.

- Usage: `Usage: asa v5 campaigns delete [OPTIONS] [CAMPAIGN_ID]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `CAMPAIGN_ID` | no | `integer` | — | — |  |
| option | `--all-unmanaged` | no | `boolean` | `False` | — | Delete all unmanaged campaigns |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns enable`

Enable a campaign or all managed campaigns.

- Usage: `Usage: asa v5 campaigns enable [OPTIONS] [CAMPAIGN_ID]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `CAMPAIGN_ID` | no | `integer` | — | — |  |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Enable all managed campaigns |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns list`

List all campaigns.

- Usage: `Usage: asa v5 campaigns list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--all`, `-a` | no | `boolean` | `False` | — | Show all campaigns, not just ASA CLI managed |
| option | `--filter`, `-f` | no | `text` | — | — | Filter campaigns by name |
| option | `--status`, `-s` | no | `text` | — | — | Filter by status (RUNNING, PAUSED) |
| option | `--type`, `-t` | no | `text` | — | — | Filter by type (brand, category, competitor, discovery) |
| option | `--bids`, `-b` | no | `boolean` | `False` | — | Show ad group default bids (slower) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns pause`

Pause a campaign or all managed campaigns.

- Usage: `Usage: asa v5 campaigns pause [OPTIONS] [CAMPAIGN_ID]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `CAMPAIGN_ID` | no | `integer` | — | — |  |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Pause all managed campaigns |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns setup`

Set up the 4-campaign structure (Brand, Category, Competitor, Discovery).

- Usage: `Usage: asa v5 campaigns setup [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--countries`, `-c` | no | `text` | `US` | — | Comma-separated country codes |
| option | `--budget`, `-b` | no | `float` | `50.0` | — | Daily budget per campaign (USD) |
| option | `--bid` | no | `float` | `1.5` | — | Default keyword bid (USD) |
| option | `--dry-run`, `-n` | no | `boolean` | `False` | — | Preview without creating |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 campaigns update`

Update a campaign's name, budget, lifetime budget, or status.

- Usage: `Usage: asa v5 campaigns update [OPTIONS] CAMPAIGN_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `CAMPAIGN_ID` | yes | `integer` | — | — |  |
| option | `--name`, `-n` | no | `text` | — | — | New campaign name |
| option | `--budget`, `-b` | no | `float` | — | — | New daily budget (USD) |
| option | `--lifetime-budget`, `-L` | no | `float` | — | — | New lifetime budget (USD). NOTE: Apple is discontinuing lifetime budgets on 2026-06-16; prefer --clear-lifetime. |
| option | `--clear-lifetime` | no | `boolean` | `False` | — | Remove the lifetime budget cap on the campaign (sets budgetAmount=null). Use this to unblock campaigns that silently stopped serving after hitting their lifetime cap. |
| option | `--status`, `-s` | no | `text` | — | — | New status (ENABLED or PAUSED) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config add-app`

Add a new app to the multi-app configuration.

- Usage: `Usage: asa v5 config add-app [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config list-apps`

List all configured apps.

- Usage: `Usage: asa v5 config list-apps [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config remove-app`

Remove an app from the configuration.

- Usage: `Usage: asa v5 config remove-app [OPTIONS] SLUG`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `SLUG` | yes | `text` | — | — |  |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config setup`

Set up API credentials and app configuration.

- Usage: `Usage: asa v5 config setup [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--credentials`, `-c` | no | `boolean` | `False` | — | Only configure credentials |
| option | `--app`, `-a` | no | `boolean` | `False` | — | Only configure app settings |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config show`

Display current configuration.

- Usage: `Usage: asa v5 config show [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config switch`

Switch the active app.

- Usage: `Usage: asa v5 config switch [OPTIONS] SLUG`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `SLUG` | yes | `text` | — | — |  |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 config test`

Test API access; exits nonzero on authentication or transport failure.

- Usage: `Usage: asa v5 config test [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 geo search`

Search for geo locations (countries, states, cities).

- Usage: `Usage: asa v5 geo search [OPTIONS] QUERY`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `QUERY` | yes | `text` | — | — |  |
| option | `--entity`, `-e` | no | `text` | — | — | Entity type: Country, AdminArea, or Locality |
| option | `--country`, `-c` | no | `text` | `US` | — | Country code to search within |
| option | `--limit`, `-l` | no | `integer` | `20` | — | Maximum results to return |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 geo set`

Set country targeting for a campaign.

- Usage: `Usage: asa v5 geo set [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | yes | `integer` | — | — | Campaign ID |
| option | `--countries` | yes | `text` | — | — | Comma-separated country/region codes (e.g. US,CA,GB) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 geo show`

Show geo targeting for all campaigns.

- Usage: `Usage: asa v5 geo show [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords add`

Add keywords to a campaign with automatic routing.

Keywords are added to:
- The appropriate exact match campaign (brand/category/competitor)
- Discovery campaign (broad match) for mining
- Discovery campaign negative keywords (to prevent overlap)

- Usage: `Usage: asa v5 keywords add [OPTIONS] KEYWORDS`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `KEYWORDS` | yes | `text` | — | — |  |
| option | `--type`, `-t` | no | `choice` | `CampaignType.CATEGORY` | — | Campaign type: brand, category, competitor |
| option | `--bid`, `-b` | no | `float` | — | — | Bid amount (USD) |
| option | `--dry-run`, `-n` | no | `boolean` | `False` | — | Preview without adding |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords add-negatives`

Add negative keywords to block unwanted search terms.

- Usage: `Usage: asa v5 keywords add-negatives [OPTIONS] KEYWORDS`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `KEYWORDS` | yes | `text` | — | — |  |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Add to all managed campaigns |
| option | `--campaign`, `-c` | no | `integer` | — | — | Specific campaign ID |
| option | `--dry-run`, `-n` | no | `boolean` | `False` | — | Preview without adding |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords delete`

Delete keywords from a campaign.

- Usage: `Usage: asa v5 keywords delete [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--ids` | no | `text` | — | — | Comma-separated keyword IDs to delete |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords delete-negatives`

Delete negative keywords by comma-separated IDs.

- Usage: `Usage: asa v5 keywords delete-negatives [OPTIONS] IDS`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `IDS` | yes | `text` | — | — |  |
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords enable`

Enable a paused keyword or all paused keywords.

- Usage: `Usage: asa v5 keywords enable [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--keyword`, `-k` | no | `integer` | — | — | Keyword ID |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Enable all paused keywords in the ad group |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords find`

Search targeting keywords across a campaign.

- Usage: `Usage: asa v5 keywords find [OPTIONS] QUERY`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `QUERY` | yes | `text` | — | — |  |
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords list`

List keywords in a campaign or ad group.

- Usage: `Usage: asa v5 keywords list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--negatives`, `-n` | no | `boolean` | `False` | — | Show negative keywords |
| option | `--filter`, `-f` | no | `text` | — | — | Filter keywords containing text |
| option | `--status`, `-s` | no | `text` | — | — | Filter by status (ACTIVE, PAUSED) |
| option | `--match-type`, `-m` | no | `text` | — | — | Filter by match type (EXACT, BROAD) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords list-negatives`

List negative keywords for a campaign (campaign + ad-group level).

- Usage: `Usage: asa v5 keywords list-negatives [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords pause`

Pause a keyword or all active keywords.

- Usage: `Usage: asa v5 keywords pause [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--keyword`, `-k` | no | `integer` | — | — | Keyword ID |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Pause all active keywords in the ad group |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords promote`

Promote keywords from Discovery to exact match campaigns.

This command:
1. Adds keywords as EXACT match to the target campaign
2. Adds them as negatives in Discovery (to stop paying for broad)

- Usage: `Usage: asa v5 keywords promote [OPTIONS] KEYWORDS`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `KEYWORDS` | yes | `text` | — | — |  |
| option | `--target`, `-t` | no | `choice` | `CampaignType.CATEGORY` | — | Target campaign type: brand, category, competitor |
| option | `--bid`, `-b` | no | `float` | — | — | Bid amount (USD) |
| option | `--dry-run`, `-n` | no | `boolean` | `False` | — | Preview without changes |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords research`

Research keywords — get Apple's recommendations and search popularity scores.

Uses ASA API targeting keyword recommendations endpoint to find new keywords
and get bid recommendations for existing ones.

- Usage: `Usage: asa v5 keywords research [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--seed`, `-s` | no | `text` | — | — | Comma-separated seed keywords for recommendations |
| option | `--limit`, `-l` | no | `integer` | `50` | — | Max results to show |
| option | `--raw` | no | `boolean` | `False` | — | Show raw API response for debugging |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords update-bid`

Update bid amount for a keyword.

- Usage: `Usage: asa v5 keywords update-bid [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--keyword`, `-k` | no | `integer` | — | — | Keyword ID |
| option | `--bid`, `-b` | yes | `float` | — | — | New bid amount (USD) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 keywords update-bids-bulk`

Update all keyword bids in a campaign/ad group at once.

- Usage: `Usage: asa v5 keywords update-bids-bulk [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--bid`, `-b` | yes | `float` | — | — | New bid amount (USD) for all keywords |
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--ad-group`, `-g` | no | `integer` | — | — | Ad group ID |
| option | `--force`, `-f` | no | `boolean` | `False` | — | Skip confirmation prompt |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 optimize`

Automated campaign optimization

- Usage: `Usage: asa v5 optimize [OPTIONS] COMMAND [ARGS]...`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--days`, `-d` | no | `integer` | `14` | — | Days to analyze |
| option | `--cpa-threshold`, `-c` | no | `float` | `5.0` | — | Max CPA for winners (USD) |
| option | `--min-installs`, `-i` | no | `integer` | `2` | — | Min installs to promote |
| option | `--min-spend`, `-s` | no | `float` | `1.0` | — | Min spend to consider blocking (USD) |
| option | `--min-impressions` | no | `integer` | `0` | — | Min impressions to consider a term |
| option | `--exclude`, `-e` | no | `text` | — | — | Comma-separated terms to exclude from analysis |
| option | `--dry-run`, `-n` | no | `boolean` | `False` | — | Preview changes without applying |
| option | `--auto-approve`, `-y` | no | `boolean` | `False` | — | Skip confirmation prompts |
| option | `--target`, `-t` | no | `text` | `category` | — | Target campaign for promotions: brand, category, competitor |
| option | `--negative-scope` | no | `text` | `discovery` | — | Where to add loser negatives: discovery or managed |
| option | `--json` | no | `boolean` | `False` | — | Output results as JSON (implies --dry-run) |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports adgroups`

Show ad group performance report.

- Usage: `Usage: asa v5 reports adgroups [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--days`, `-d` | no | `integer` | `30` | — | Number of days |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Show ad groups for all campaigns |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports ads`

Show ad performance over exact completed calendar dates.

- Usage: `Usage: asa v5 reports ads [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--days`, `-d` | no | `integer` | `14` | — | Number of days |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Show ad report for all campaigns |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports bid-recommendations`

Show Apple's suggested bid amounts vs current bids for keywords.

For each campaign and ad group, fetches the keyword report with bid
recommendation insights. Displays a color-coded table showing where
your bids are below Apple's suggestions.

- Usage: `Usage: asa v5 reports bid-recommendations [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--days`, `-d` | no | `integer` | `14` | — | Number of days |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Show bids for all campaigns |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports custom`

Create a custom impression share report, poll until complete, and display results.

- Usage: `Usage: asa v5 reports custom [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--days`, `-d` | no | `integer` | `30` | — | Number of days (max 30) |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--name`, `-n` | no | `text` | `Impression Share Report` | — | Report name |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports custom-get`

Get a specific custom report status and results.

- Usage: `Usage: asa v5 reports custom-get [OPTIONS] REPORT_ID`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| argument | `REPORT_ID` | yes | `text` | — | — |  |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports custom-list`

List all custom reports.

- Usage: `Usage: asa v5 reports custom-list [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports impression-share`

Fetch Apple's true async impression-share report and download its CSV.

- Usage: `Usage: asa v5 reports impression-share [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Resolve the advertised app from a campaign |
| option | `--adam-id` | no | `integer` | — | — | Filter to an App Store Adam ID |
| option | `--countries` | no | `text` | — | — | Comma-separated country or region codes |
| option | `--days`, `-d` | no | `integer` | `30` | — | Number of completed days (max 30) |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--report-id` | no | `text` | — | — | Reuse an existing custom report instead of creating one |
| option | `--all` | no | `boolean` | `False` | — | Do not filter the organization by app |
| option | `--wait`, `--no-wait` | no | `boolean` | `True` | — | Wait for and download report results |
| option | `--poll-interval` | no | `float range` | `5.0` | — | Polling seconds |
| option | `--timeout` | no | `integer range` | `300` | — | Maximum wait seconds |
| option | `--limit`, `-l` | no | `integer` | `0` | — | Max rows (0 means all) |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports keywords`

Show keyword performance over exact completed calendar dates.

- Usage: `Usage: asa v5 reports keywords [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--days`, `-d` | no | `integer` | `30` | — | Number of days |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--min-impressions` | no | `integer` | `0` | — | Minimum impressions filter |
| option | `--sort`, `-s` | no | `text` | `spend` | — | Sort by: spend, impressions, taps, installs, cpa |
| option | `--limit`, `-l` | no | `integer` | `50` | — | Max keywords to show |
| option | `--all`, `-a` | no | `boolean` | `False` | — | Report every scoped campaign |
| option | `--include-zero` | no | `boolean` | `False` | — | Merge complete targeting-keyword inventory, including zero-activity rows |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports search-terms`

Show search terms over exact completed calendar dates.

- Usage: `Usage: asa v5 reports search-terms [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--campaign`, `-c` | no | `integer` | — | — | Campaign ID |
| option | `--days`, `-d` | no | `integer` | `14` | — | Number of days |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--min-impressions` | no | `integer` | `10` | — | Minimum impressions filter |
| option | `--winners`, `-w` | no | `boolean` | `False` | — | Show potential keywords to promote |
| option | `--negatives`, `-n` | no | `boolean` | `False` | — | Show potential negative keywords |
| option | `--limit`, `-l` | no | `integer` | `50` | — | Max terms to show |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `asa v5 reports summary`

Show campaign performance over exact completed calendar dates.

- Usage: `Usage: asa v5 reports summary [OPTIONS]`

### Inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--days`, `-d` | no | `integer` | `30` | — | Number of days to report |
| option | `--start`, `--start-date` | no | `text` | — | — | Inclusive start date (YYYY-MM-DD) |
| option | `--end`, `--end-date` | no | `text` | — | — | Inclusive complete end date (YYYY-MM-DD) |
| option | `--all`, `-a`, `--managed-only` | no | `boolean` | `True` | — | Include all campaigns (default) or only managed |
| option | `--json` | no | `boolean` | `False` | — | Emit stable machine-readable JSON |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
