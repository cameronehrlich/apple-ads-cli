<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Reports

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`apps_ad_reports`](#apps-ad-reports)
- [`apps_ad_group_reports`](#apps-ad-group-reports)
- [`apps_campaign_reports`](#apps-campaign-reports)
- [`apps_keyword_reports`](#apps-keyword-reports)
- [`apps_search_term_reports`](#apps-search-term-reports)
- [`brands_ad_reports`](#brands-ad-reports)
- [`brands_ad_group_reports`](#brands-ad-group-reports)
- [`brands_campaign_reports`](#brands-campaign-reports)
- [`brands_keyword_reports`](#brands-keyword-reports)
- [`brands_search_term_reports`](#brands-search-term-reports)

## `apps_ad_reports`

- Status: `implemented`
- Canonical command: `asa reports-apps ad`
- Usage: `Usage: asa reports-apps ad [OPTIONS]`
- SDK contract: `POST /reports/apps/ads/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, apps_reporting_request`
- Body parameters: `[{"annotation":"AppsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.apps_reporting_request.AppsReportingRequest","name":"apps_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `AppsAdReportResponse`
- CLI help: Ad reports apps.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.apps_reporting_request.AppsReportingRequest`

Request body for APPS promoted object type. Supported groupBy values: deviceClass, ageRange, gender, countryCode, adminArea, locality, storefront, countryOrRegion. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude ageRange, gender, countryCode, adminArea, locality).

- Schema SHA-256: `10529c85b8733b7ac3cee1046fb62d14514a4241a37328ee0505b040b15b6506`
- Source SHA-256: `26d535cae1545f1e6a3b45595adf9710004ddae0c8bf9cc0b52c35081fd0e1e8`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for APPS. Note: KEYWORD and SEARCHTERM entities exclude ageRange, gender, countryCode, adminArea, locality. AD entity additionally excludes deviceClass. HOURLY granularity excludes ageRange, gender, countryCode, adminArea, locality. |
| `options` | no | `AppsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `AppsOptions`

Report options for APPS promoted object type.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. EMPTY_METRICS includes rows with zero metrics. Not supported for the SEARCHTERM entity. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `apps_ad_group_reports`

- Status: `implemented`
- Canonical command: `asa reports-apps ad-group`
- Usage: `Usage: asa reports-apps ad-group [OPTIONS]`
- SDK contract: `POST /reports/apps/adgroups/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, apps_reporting_request`
- Body parameters: `[{"annotation":"AppsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.apps_reporting_request.AppsReportingRequest","name":"apps_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `AppsAdGroupReportResponse`
- CLI help: Ad group reports apps.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.apps_reporting_request.AppsReportingRequest`

Request body for APPS promoted object type. Supported groupBy values: deviceClass, ageRange, gender, countryCode, adminArea, locality, storefront, countryOrRegion. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude ageRange, gender, countryCode, adminArea, locality).

- Schema SHA-256: `10529c85b8733b7ac3cee1046fb62d14514a4241a37328ee0505b040b15b6506`
- Source SHA-256: `26d535cae1545f1e6a3b45595adf9710004ddae0c8bf9cc0b52c35081fd0e1e8`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for APPS. Note: KEYWORD and SEARCHTERM entities exclude ageRange, gender, countryCode, adminArea, locality. AD entity additionally excludes deviceClass. HOURLY granularity excludes ageRange, gender, countryCode, adminArea, locality. |
| `options` | no | `AppsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `AppsOptions`

Report options for APPS promoted object type.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. EMPTY_METRICS includes rows with zero metrics. Not supported for the SEARCHTERM entity. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `apps_campaign_reports`

- Status: `implemented`
- Canonical command: `asa reports-apps campaign`
- Usage: `Usage: asa reports-apps campaign [OPTIONS]`
- SDK contract: `POST /reports/apps/campaigns/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, apps_reporting_request`
- Body parameters: `[{"annotation":"AppsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.apps_reporting_request.AppsReportingRequest","name":"apps_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `AppsCampaignReportResponse`
- CLI help: Campaign reports apps.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.apps_reporting_request.AppsReportingRequest`

Request body for APPS promoted object type. Supported groupBy values: deviceClass, ageRange, gender, countryCode, adminArea, locality, storefront, countryOrRegion. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude ageRange, gender, countryCode, adminArea, locality).

- Schema SHA-256: `10529c85b8733b7ac3cee1046fb62d14514a4241a37328ee0505b040b15b6506`
- Source SHA-256: `26d535cae1545f1e6a3b45595adf9710004ddae0c8bf9cc0b52c35081fd0e1e8`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for APPS. Note: KEYWORD and SEARCHTERM entities exclude ageRange, gender, countryCode, adminArea, locality. AD entity additionally excludes deviceClass. HOURLY granularity excludes ageRange, gender, countryCode, adminArea, locality. |
| `options` | no | `AppsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `AppsOptions`

Report options for APPS promoted object type.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. EMPTY_METRICS includes rows with zero metrics. Not supported for the SEARCHTERM entity. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `apps_keyword_reports`

- Status: `implemented`
- Canonical command: `asa reports-apps keyword`
- Usage: `Usage: asa reports-apps keyword [OPTIONS]`
- SDK contract: `POST /reports/apps/keywords/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, apps_reporting_request`
- Body parameters: `[{"annotation":"AppsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.apps_reporting_request.AppsReportingRequest","name":"apps_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `AppsKeywordReportResponse`
- CLI help: Keyword reports apps.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.apps_reporting_request.AppsReportingRequest`

Request body for APPS promoted object type. Supported groupBy values: deviceClass, ageRange, gender, countryCode, adminArea, locality, storefront, countryOrRegion. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude ageRange, gender, countryCode, adminArea, locality).

- Schema SHA-256: `10529c85b8733b7ac3cee1046fb62d14514a4241a37328ee0505b040b15b6506`
- Source SHA-256: `26d535cae1545f1e6a3b45595adf9710004ddae0c8bf9cc0b52c35081fd0e1e8`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for APPS. Note: KEYWORD and SEARCHTERM entities exclude ageRange, gender, countryCode, adminArea, locality. AD entity additionally excludes deviceClass. HOURLY granularity excludes ageRange, gender, countryCode, adminArea, locality. |
| `options` | no | `AppsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `AppsOptions`

Report options for APPS promoted object type.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. EMPTY_METRICS includes rows with zero metrics. Not supported for the SEARCHTERM entity. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `apps_search_term_reports`

- Status: `implemented`
- Canonical command: `asa reports-apps search-term`
- Usage: `Usage: asa reports-apps search-term [OPTIONS]`
- SDK contract: `POST /reports/apps/searchterms/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, apps_reporting_request`
- Body parameters: `[{"annotation":"AppsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.apps_reporting_request.AppsReportingRequest","name":"apps_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `AppsSearchTermReportResponse`
- CLI help: Search term reports apps.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.apps_reporting_request.AppsReportingRequest`

Request body for APPS promoted object type. Supported groupBy values: deviceClass, ageRange, gender, countryCode, adminArea, locality, storefront, countryOrRegion. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude ageRange, gender, countryCode, adminArea, locality).

- Schema SHA-256: `10529c85b8733b7ac3cee1046fb62d14514a4241a37328ee0505b040b15b6506`
- Source SHA-256: `26d535cae1545f1e6a3b45595adf9710004ddae0c8bf9cc0b52c35081fd0e1e8`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for APPS. Note: KEYWORD and SEARCHTERM entities exclude ageRange, gender, countryCode, adminArea, locality. AD entity additionally excludes deviceClass. HOURLY granularity excludes ageRange, gender, countryCode, adminArea, locality. |
| `options` | no | `AppsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `AppsOptions`

Report options for APPS promoted object type.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. EMPTY_METRICS includes rows with zero metrics. Not supported for the SEARCHTERM entity. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `brands_ad_reports`

- Status: `implemented`
- Canonical command: `asa reports-business-brands ad`
- Usage: `Usage: asa reports-business-brands ad [OPTIONS]`
- SDK contract: `POST /reports/business-brands/ads/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, brands_reporting_request`
- Body parameters: `[{"annotation":"BrandsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest","name":"brands_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `BrandsAdReportResponse`
- CLI help: Ad reports business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest`

Request body for BRANDS promoted object type. Supported groupBy values: deviceClass, locationId, supplyPlacement. EMPTY_METRICS is not supported for any BRANDS entity on external calls. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude supplyPlacement; LOCATION excludes supplyPlacement and locationId).

- Schema SHA-256: `90a4544a0c01ffe142874ccb6e8301c5d1c2756fdb545e263b16ea7f9073a480`
- Source SHA-256: `25beb7092f12b1467978286d7017c6e7d7a0f9a1d28d7924c6d4a48ffa05c92e`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for BRANDS. Note: KEYWORD and SEARCHTERM entities exclude supplyPlacement. LOCATION entity excludes supplyPlacement and locationId. |
| `options` | no | `BrandsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `BrandsOptions`

Report options for BRANDS promoted object type. EMPTY_METRICS is not supported for any BRANDS entity on external calls.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `brands_ad_group_reports`

- Status: `implemented`
- Canonical command: `asa reports-business-brands ad-group`
- Usage: `Usage: asa reports-business-brands ad-group [OPTIONS]`
- SDK contract: `POST /reports/business-brands/adgroups/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, brands_reporting_request`
- Body parameters: `[{"annotation":"BrandsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest","name":"brands_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `BrandsAdGroupReportResponse`
- CLI help: Ad group reports business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest`

Request body for BRANDS promoted object type. Supported groupBy values: deviceClass, locationId, supplyPlacement. EMPTY_METRICS is not supported for any BRANDS entity on external calls. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude supplyPlacement; LOCATION excludes supplyPlacement and locationId).

- Schema SHA-256: `90a4544a0c01ffe142874ccb6e8301c5d1c2756fdb545e263b16ea7f9073a480`
- Source SHA-256: `25beb7092f12b1467978286d7017c6e7d7a0f9a1d28d7924c6d4a48ffa05c92e`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for BRANDS. Note: KEYWORD and SEARCHTERM entities exclude supplyPlacement. LOCATION entity excludes supplyPlacement and locationId. |
| `options` | no | `BrandsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `BrandsOptions`

Report options for BRANDS promoted object type. EMPTY_METRICS is not supported for any BRANDS entity on external calls.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `brands_campaign_reports`

- Status: `implemented`
- Canonical command: `asa reports-business-brands campaign`
- Usage: `Usage: asa reports-business-brands campaign [OPTIONS]`
- SDK contract: `POST /reports/business-brands/campaigns/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, brands_reporting_request`
- Body parameters: `[{"annotation":"BrandsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest","name":"brands_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `BrandsCampaignReportResponse`
- CLI help: Campaign reports business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest`

Request body for BRANDS promoted object type. Supported groupBy values: deviceClass, locationId, supplyPlacement. EMPTY_METRICS is not supported for any BRANDS entity on external calls. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude supplyPlacement; LOCATION excludes supplyPlacement and locationId).

- Schema SHA-256: `90a4544a0c01ffe142874ccb6e8301c5d1c2756fdb545e263b16ea7f9073a480`
- Source SHA-256: `25beb7092f12b1467978286d7017c6e7d7a0f9a1d28d7924c6d4a48ffa05c92e`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for BRANDS. Note: KEYWORD and SEARCHTERM entities exclude supplyPlacement. LOCATION entity excludes supplyPlacement and locationId. |
| `options` | no | `BrandsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `BrandsOptions`

Report options for BRANDS promoted object type. EMPTY_METRICS is not supported for any BRANDS entity on external calls.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `brands_keyword_reports`

- Status: `implemented`
- Canonical command: `asa reports-business-brands keyword`
- Usage: `Usage: asa reports-business-brands keyword [OPTIONS]`
- SDK contract: `POST /reports/business-brands/keywords/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, brands_reporting_request`
- Body parameters: `[{"annotation":"BrandsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest","name":"brands_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `BrandsKeywordReportResponse`
- CLI help: Keyword reports business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest`

Request body for BRANDS promoted object type. Supported groupBy values: deviceClass, locationId, supplyPlacement. EMPTY_METRICS is not supported for any BRANDS entity on external calls. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude supplyPlacement; LOCATION excludes supplyPlacement and locationId).

- Schema SHA-256: `90a4544a0c01ffe142874ccb6e8301c5d1c2756fdb545e263b16ea7f9073a480`
- Source SHA-256: `25beb7092f12b1467978286d7017c6e7d7a0f9a1d28d7924c6d4a48ffa05c92e`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for BRANDS. Note: KEYWORD and SEARCHTERM entities exclude supplyPlacement. LOCATION entity excludes supplyPlacement and locationId. |
| `options` | no | `BrandsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `BrandsOptions`

Report options for BRANDS promoted object type. EMPTY_METRICS is not supported for any BRANDS entity on external calls.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |

## `brands_search_term_reports`

- Status: `implemented`
- Canonical command: `asa reports-business-brands search-term`
- Usage: `Usage: asa reports-business-brands search-term [OPTIONS]`
- SDK contract: `POST /reports/business-brands/searchterms/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, brands_reporting_request`
- Body parameters: `[{"annotation":"BrandsReportingRequest","container":"model","default":null,"model":"apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest","name":"brands_reporting_request","required":true,"wire_name":"body"}]`
- Returns: `BrandsSearchTermReportResponse`
- CLI help: Search term reports business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.brands_reporting_request.BrandsReportingRequest`

Request body for BRANDS promoted object type. Supported groupBy values: deviceClass, locationId, supplyPlacement. EMPTY_METRICS is not supported for any BRANDS entity on external calls. Entity-specific groupBy restrictions apply server-side (e.g. KEYWORD and SEARCHTERM exclude supplyPlacement; LOCATION excludes supplyPlacement and locationId).

- Schema SHA-256: `90a4544a0c01ffe142874ccb6e8301c5d1c2756fdb545e263b16ea7f9073a480`
- Source SHA-256: `25beb7092f12b1467978286d7017c6e7d7a0f9a1d28d7924c6d4a48ffa05c92e`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fields` | no | `array[string] | null` | `None` |  |
| `filters` | no | `array[Filter] | null` | `None` |  |
| `groupBy` | no | `array[string] | null` | `None` | Supported values for BRANDS. Note: KEYWORD and SEARCHTERM entities exclude supplyPlacement. LOCATION entity excludes supplyPlacement and locationId. |
| `options` | no | `BrandsOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` |  |
| `timeRange` | no | `TimeRange | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "fields": [
    "<string>"
  ],
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "groupBy": [
    "<string>"
  ],
  "options": {
    "includeRows": [
      "<string>"
    ]
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>",
    "timeZone": "<string>"
  }
}
```

#### Referenced structures

##### `BrandsOptions`

Report options for BRANDS promoted object type. EMPTY_METRICS is not supported for any BRANDS entity on external calls.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `includeRows` | no | `array[string] | null` | `None` | GRAND_TOTAL includes a summary row with aggregated totals. |

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `RequestPagination`

RequestPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` | Maximum 5000. Default 100. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |

##### `TimeRange`

TimeRange

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | no | `string | null` | `None` | End date in YYYY-MM-DD format. For WEEKLY granularity: must be at least 14 days in the past. For MONTHLY granularity: must be at least 90 days in the past. |
| `granularity` | no | `string | null` | `None` | Time granularity for the report rows. HOURLY: Not supported for SEARCHTERM or AD entities. Date range must start within the last 7 days. DAILY: Date range start must be within the last 90 days. WEEKLY: Date range start within the last 365 days; end date at least 14 days in the past. MONTHLY: End date must be at least 90 days in the past. |
| `start` | no | `string | null` | `None` | Start date in YYYY-MM-DD format. For HOURLY granularity: must be within the last 7 days. For DAILY granularity: must be within the last 90 days. For WEEKLY granularity: must be within the last 365 days. |
| `timeZone` | no | `string | null` | `ORTZ` | Timezone for the report date range. ORTZ uses the ad account's local timezone. Note: UTC is not supported for the SEARCHTERM entity (both APPS and BRANDS). |
