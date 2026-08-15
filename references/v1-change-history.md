<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Change history

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`get_change_details`](#get-change-details)
- [`query_audit_summary`](#query-audit-summary)

## `get_change_details`

- Status: `implemented`
- Canonical command: `asa change-history get`
- Usage: `Usage: asa change-history get [OPTIONS]`
- SDK contract: `GET /change-history/{detailId}`
- Context: `required`
- Mutation: `no`
- Pagination: `offset-limit`
- Required SDK parameters: `x_ap_context, detail_id`
- Body parameters: `[]`
- Returns: `ChangeDetailsResponse`
- CLI help: Get change history.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--detail-id` | yes | `text` | — | — | detailId parameter |
| option | `--limit` | no | `integer` | — | — | limit parameter |
| option | `--offset` | no | `integer` | — | — | offset parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `query_audit_summary`

- Status: `implemented`
- Canonical command: `asa change-history query`
- Usage: `Usage: asa change-history query [OPTIONS]`
- SDK contract: `POST /change-history/query`
- Context: `required`
- Mutation: `no`
- Pagination: `audit-pagination`
- Required SDK parameters: `x_ap_context, audit_query`
- Body parameters: `[{"annotation":"AuditQuery","container":"model","default":null,"model":"apple_ads_platform.models.audit_query.AuditQuery","name":"audit_query","required":true,"wire_name":"body"}]`
- Returns: `AuditSummaryResponse`
- CLI help: Query change history.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.audit_query.AuditQuery`

AuditQuery

- Schema SHA-256: `6badd2689485f5deaab4e06236d456f64e0330c08aea933ab405cf5b31afee97`
- Source SHA-256: `20e15f10ac1bdbc7e01fb6a0d4f6effe95007e2e859b9c5b9b0dd2da714664cf`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[AuditFilter] | null` | `None` |  |
| `options` | no | `AuditQueryOptions | null` | `None` |  |
| `pagination` | no | `Pagination | null` | `None` |  |
| `sorting` | no | `array[AuditSorting] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | IN | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | unknown_default_open_api>",
      "value": "<string>"
    }
  ],
  "options": {
    "metadata": "<string>",
    "needTotals": "<string>",
    "timeZone": "<string>"
  },
  "pagination": {
    "offset": 0,
    "pageSize": 0,
    "totalCount": 0
  },
  "sorting": [
    {
      "field": "<string>",
      "order": "<one of: ASC | DESC | unknown_default_open_api>"
    }
  ]
}
```

#### Referenced structures

##### `AuditFilter`

Filter object

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` | The field to filter on. Standard event fields are always available (`eventTime`, `entityType`, `entityId`, `userId`, `userType`, `txnId`). Some filterable identifiers vary by `entityType` because each event carries its parent's id under a type-specific name: * `Campaign`, `AdGroup` → `adAccountId` * `AdGroup`, `Keyword`, `NegativeKeyword` → `campaignId` * `AdGroup`, `Keyword`, `NegativeKeyword` → `adGroupId` For non-time fields only `EQUALS` and `IN` are supported; `GREATER_THAN` / `LESS_THAN` / `BETWEEN` are reserved for `eventTime`. |
| `operator` | no | `AuditOperator | null` | `None` |  |
| `value` | no | `any | null` | `None` | single value (long/integer or string or datetime ) or array of (long/integer or string or datetime ) |

##### `AuditOperator`

operator enum

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `AuditQueryOptions`

Key-value query options

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `metadata` | no | `string | null` | `none` | Controls which entity metadata is included in change detail responses. none — no metadata. latest — join current entity_meta (may differ from time of change). snapshot — use metadata captured at snapshot time. |
| `needTotals` | no | `string | null` | `true` | Skip the expensive COUNT query when set to "false". Pagination.totalCount will be 0 in the response. |
| `timeZone` | no | `string | null` | `None` | Timezone for eventTime filters. UTC — filter values are in UTC (default). ORTZ — filter values are in the org's configured timezone; converted to UTC server-side. |

##### `AuditSortOrder`

AuditSortOrder

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `AuditSorting`

sorting

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `AuditSortOrder | null` | `None` |  |

##### `Pagination`

Pagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` |  |
| `totalCount` | no | `integer | null` | `None` |  |
