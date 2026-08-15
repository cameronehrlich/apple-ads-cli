<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Insights

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`impression_share_query`](#impression-share-query)
- [`search_term_popularity_query`](#search-term-popularity-query)

## `impression_share_query`

- Status: `implemented`
- Canonical command: `asa insights impression-share`
- Usage: `Usage: asa insights impression-share [OPTIONS]`
- SDK contract: `POST /insights/apps/impression-share/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, impression_share_query_request`
- Body parameters: `[{"annotation":"ImpressionShareQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.impression_share_query_request.ImpressionShareQueryRequest","name":"impression_share_query_request","required":true,"wire_name":"body"}]`
- Returns: `ImpressionShareQueryResponse`
- CLI help: Impression share insights.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.impression_share_query_request.ImpressionShareQueryRequest`

Request body for the impression share query endpoint. A filter on promotedObjectId is mandatory. Timezone is fixed to UTC.

- Schema SHA-256: `e06408e61fc33b2f61969132aefcb8e5d156b772bc0fed67888e84e9bd4d13c3`
- Source SHA-256: `7db1b9be82438f0b70ef2c48a6ad828d37f7b5998a0a4d3a2cacf06f050aab99`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | yes | `array[Filter]` | — | Filter conditions. At minimum, a promotedObjectId filter must be provided. |
| `options` | no | `ImpressionShareOptions | null` | `None` |  |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` | Sort criteria. Maximum 2 sort fields. |
| `timeRange` | yes | `ImpressionShareTimeRange` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ],
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>"
  }
}
```

#### Referenced structures

##### `Filter`

Filter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `operator` | no | `string | null` | `None` |  |
| `value` | no | `any | null` | `None` | For single-value operators (EQUALS, NOT_EQUALS, GREATER_THAN, etc.), pass either a bare string or a single-element array. For multi-value operators (IN, BETWEEN, CONTAINS_ANY, CONTAINS_ALL), pass an array. Operator-specific cardinality is enforced server-side. |

##### `ImpressionShareOptions`

Report options for impression share queries.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `impressionShareReportType` | no | `string | null` | `FIRST_SLOT` | FIRST_SLOT: impression share and metrics for the first (top) ad position only. ALL_SLOTS: impression share and metrics aggregated across all ad positions. |

##### `ImpressionShareTimeRange`

Time range for impression share queries. Timezone is fixed to UTC.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | yes | `string` | — | End date in YYYY-MM-DD format. |
| `granularity` | yes | `string` | — | DAILY: daily aggregation, uses day date field. WEEKLY_SUN_SAT: fixed weekly aggregation (Sunday-Saturday), uses week date field. |
| `start` | yes | `string` | — | Start date in YYYY-MM-DD format. |
| `timeZone` | no | `string | null` | `UTC` | Fixed to UTC. Not user-configurable. |

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

## `search_term_popularity_query`

- Status: `implemented`
- Canonical command: `asa insights search-term-popularity`
- Usage: `Usage: asa insights search-term-popularity [OPTIONS]`
- SDK contract: `POST /insights/apps/search-term-popularity/query`
- Context: `required`
- Mutation: `no`
- Pagination: `request-pagination`
- Required SDK parameters: `x_ap_context, search_term_popularity_query_request`
- Body parameters: `[{"annotation":"SearchTermPopularityQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.search_term_popularity_query_request.SearchTermPopularityQueryRequest","name":"search_term_popularity_query_request","required":true,"wire_name":"body"}]`
- Returns: `SearchTermPopularityQueryResponse`
- CLI help: Search term popularity insights.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.search_term_popularity_query_request.SearchTermPopularityQueryRequest`

Request body for the search term popularity query endpoint. Timezone is fixed to UTC.

- Schema SHA-256: `f1b79bece8a3c57deeaed8dbefc2a6a0deb052d93bdfb6dbb757e8aafdfe6f56`
- Source SHA-256: `ab5fdd93f3a6c6138f42d65af0b50a9922066fa00e63c881bff19f99fcb683d9`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[Filter] | null` | `None` | Filter conditions to narrow results. |
| `pagination` | no | `RequestPagination | null` | `None` |  |
| `sorting` | no | `array[Sorting] | null` | `None` | Sort criteria. Maximum 2 sort fields. Default genre ASC, rankInGenre ASC. |
| `timeRange` | yes | `SearchTermPopularityTimeRange` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "timeRange": {
    "end": "<string>",
    "granularity": "<string>",
    "start": "<string>"
  }
}
```

#### Referenced structures

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

##### `SearchTermPopularityTimeRange`

Time range for search term popularity queries. Timezone is fixed to UTC.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `end` | yes | `string` | — | End date. For WEEKLY_SUN_SAT: YYYY-MM-DD format. For MONTHLY: YYYY-MM-DD format. |
| `granularity` | yes | `string` | — | WEEKLY_SUN_SAT: fixed weekly reports (Sunday-Saturday). Generated Mondays at 07:00 UTC. Rolling 65-week retention. MONTHLY: calendar month snapshots. Refreshes on the 5th of each month UTC. Rolling 15-month retention. |
| `start` | yes | `string` | — | Start date. For WEEKLY_SUN_SAT: YYYY-MM-DD format. For MONTHLY: YYYY-MM-DD format. |
| `timeZone` | no | `string | null` | `UTC` | Fixed to UTC. Not user-configurable. |

##### `Sorting`

Sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `string | null` | `None` |  |
