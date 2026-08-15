<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Campaigns

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`campaigns_post`](#campaigns-post)
- [`campaigns_id_delete`](#campaigns-id-delete)
- [`campaigns_id_get`](#campaigns-id-get)
- [`campaigns_id_legacy_app_limited_status_reason_details_get`](#campaigns-id-legacy-app-limited-status-reason-details-get)
- [`campaigns_query_post`](#campaigns-query-post)
- [`campaigns_id_put`](#campaigns-id-put)

## `campaigns_post`

- Status: `implemented`
- Canonical command: `asa campaigns create`
- Usage: `Usage: asa campaigns create [OPTIONS]`
- SDK contract: `POST /campaigns`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[CampaignCreate]","container":"model","default":"None","model":"apple_ads_platform.models.campaign_create.CampaignCreate","name":"campaign_create","required":false,"wire_name":"body"}]`
- Returns: `CampaignResponse`
- CLI help: Create campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.campaign_create.CampaignCreate`

CampaignCreate

- Schema SHA-256: `e1b563f0e8a44685a350543ebef9fe1254c6b164daee479191ddee4c4aaf2812`
- Source SHA-256: `810b2ffaaf0f57c7491662396e2c84e9df62c00349a14dd35f917ac36a3bbd49`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adAccountId` | yes | `integer` | — |  |
| `bidStrategy` | no | `BidStrategyCreate | null` | `None` |  |
| `billingEvent` | yes | `BillingEvent` | — |  |
| `dailyBudget` | yes | `DailyBudgetCreate` | — |  |
| `endTime` | no | `string | null` | `None` |  |
| `invoiceDetail` | no | `InvoiceDetailCreate | null` | `None` |  |
| `name` | yes | `string` | — |  |
| `promotedObjectId` | yes | `string` | — |  |
| `promotedObjectType` | yes | `PromotedObjectType` | — |  |
| `regulationResponses` | no | `array[RegulationResponseCreate] | null` | `None` |  |
| `sharedBudgets` | no | `array[SharedBudgetAssignmentCreate] | null` | `None` |  |
| `startTime` | no | `string | null` | `None` |  |
| `status` | no | `CampaignStatus | null` | `None` |  |
| `targeting` | yes | `CampaignTargetingCreate` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adAccountId": 0,
  "billingEvent": "<one of: IMPRESSIONS | INSTALLS | TAPS | unknown_default_open_api>",
  "dailyBudget": {
    "value": {
      "amount": "<string>"
    }
  },
  "name": "<string>",
  "promotedObjectId": "<string>",
  "promotedObjectType": "<one of: APPSTORE_APP | BUSINESS_BRAND | unknown_default_open_api>",
  "targeting": {
    "countryOrRegion": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "supplyPlacement": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "supplySource": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    }
  }
}
```

#### Referenced structures

##### `BidStrategyCreate`

BidStrategyCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `bid` | no | `Money | null` | `None` |  |
| `bidStrategyGoal` | no | `BidStrategyGoal | null` | `None` |  |
| `bidStrategyType` | no | `BidStrategyType | null` | `None` |  |

##### `BidStrategyGoal`

BidStrategyGoal

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `BidStrategyType`

BidStrategyType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `BillingEvent`

BillingEvent

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `CampaignStatus`

CampaignStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `CampaignTargetingCreate`

CampaignTargetingCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `countryOrRegion` | no | `TargetingDataCreate | null` | `None` |  |
| `supplyPlacement` | no | `TargetingDataCreate | null` | `None` |  |
| `supplySource` | no | `TargetingDataCreate | null` | `None` |  |

##### `DailyBudgetCreate`

DailyBudgetCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `value` | no | `Money | null` | `None` |  |

##### `InvoiceDetailCreate`

InvoiceDetailCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `billingEmail` | yes | `string` | — |  |
| `clientName` | no | `string | null` | `None` |  |
| `orderNumber` | no | `string | null` | `None` |  |
| `primaryBuyerEmail` | yes | `string` | — |  |
| `primaryBuyerName` | yes | `string` | — |  |

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

##### `PromotedObjectType`

PromotedObjectType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RegulationResponseCreate`

RegulationResponseCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `regulationType` | no | `RegulationType | null` | `None` |  |
| `responseValue` | no | `RegulationResponseValue | null` | `None` |  |

##### `RegulationResponseValue`

RegulationResponseValue

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RegulationType`

RegulationType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `SharedBudgetAssignmentCreate`

SharedBudgetAssignmentCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `budgetId` | no | `integer | null` | `None` |  |

##### `TargetingDataCreate`

TargetingDataCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `exclude` | no | `array[string] | null` | `None` |  |
| `include` | no | `array[string] | null` | `None` |  |

## `campaigns_id_delete`

- Status: `implemented`
- Canonical command: `asa campaigns delete`
- Usage: `Usage: asa campaigns delete [OPTIONS]`
- SDK contract: `DELETE /campaigns/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `campaigns_id_get`

- Status: `implemented`
- Canonical command: `asa campaigns get`
- Usage: `Usage: asa campaigns get [OPTIONS]`
- SDK contract: `GET /campaigns/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `CampaignResponse`
- CLI help: Get campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `campaigns_id_legacy_app_limited_status_reason_details_get`

- Status: `implemented`
- Canonical command: `asa campaigns legacy-app-limited-status-reasons`
- Usage: `Usage: asa campaigns legacy-app-limited-status-reasons [OPTIONS]`
- SDK contract: `GET /campaigns/{id}/legacy-app-limited-status-reason-details`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `LegacyAppLimitedStatusReasonDetailsResponse`
- CLI help: Legacy app limited status reasons campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `campaigns_query_post`

- Status: `implemented`
- Canonical command: `asa campaigns query`
- Usage: `Usage: asa campaigns query [OPTIONS]`
- SDK contract: `POST /campaigns/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `CampaignQueryResponse`
- CLI help: Query campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.query_request.QueryRequest`

QueryRequest

- Schema SHA-256: `c5943287bce3f029234c099b649270dbbf32606ba204cb6f730765833cd24d38`
- Source SHA-256: `5acc04a9e0742bd31394257f1ce62ffb4a3811a197a3f9644b9e7c09ae087c3d`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[QueryFilter] | null` | `None` |  |
| `pagination` | no | `QueryPagination | null` | `None` |  |
| `sorting` | no | `array[QuerySort] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "ignoreCase": false,
      "operator": "<one of: IS_NOT_NULL | EQUALS | STARTS_WITH | IN | NOT_CONTAINS_ANY | NOT_EQUALS | LESS_THAN_OR_EQUAL_TO | BETWEEN | NOT_IN | LESS_THAN | GREATER_THAN_OR_EQUAL_TO | CONTAINS_ALL | NOT_CONTAINS_ALL | LIKE | IS_NULL | GREATER_THAN | ENDS_WITH | CONTAINS_ANY | NOT_LIKE | unknown_default_open_api>",
      "value": "<string>"
    }
  ],
  "pagination": {
    "fetchTotalCount": false,
    "offset": 0,
    "pageSize": 0
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

##### `QueryFilter`

QueryFilter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `ignoreCase` | no | `boolean | null` | `None` |  |
| `operator` | no | `QueryFilterOperator | null` | `None` |  |
| `value` | no | `any | null` | `None` | The filter value; type depends on the field being filtered |

##### `QueryFilterOperator`

QueryFilterOperator

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `QueryPagination`

QueryPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `fetchTotalCount` | no | `boolean | null` | `False` |  |
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` |  |

##### `QuerySort`

QuerySort

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | no | `string | null` | `None` |  |
| `order` | no | `QuerySortOrder | null` | `None` |  |

##### `QuerySortOrder`

QuerySortOrder

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `campaigns_id_put`

- Status: `implemented`
- Canonical command: `asa campaigns update`
- Usage: `Usage: asa campaigns update [OPTIONS]`
- SDK contract: `PUT /campaigns/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[CampaignUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.campaign_update.CampaignUpdate","name":"campaign_update","required":false,"wire_name":"body"}]`
- Returns: `CampaignResponse`
- CLI help: Update campaigns.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.campaign_update.CampaignUpdate`

CampaignUpdate

- Schema SHA-256: `91608a246292e0272db99e4f0aa0ae1b77f5b12bfeec45a6e5d0993d4784f060`
- Source SHA-256: `6625181515ccd819d5048ff1586c5782d3a3ff36c93cf52c9df4cf869b825cac`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `bidStrategy` | no | `BidStrategyUpdate | null` | `None` |  |
| `dailyBudget` | no | `DailyBudgetUpdate | null` | `None` |  |
| `endTime` | no | `string | null` | `None` |  |
| `invoiceDetail` | no | `InvoiceDetailUpdate | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |
| `regulationResponses` | no | `array[RegulationResponseUpdate] | null` | `None` |  |
| `sharedBudgets` | no | `array[SharedBudgetAssignmentUpdate] | null` | `None` |  |
| `startTime` | no | `string | null` | `None` |  |
| `status` | no | `CampaignStatus | null` | `None` |  |
| `targeting` | no | `CampaignTargetingUpdate | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "bidStrategy": {
    "bid": {
      "amount": "<string>"
    },
    "bidStrategyGoal": "<one of: IMPRESSION | INSTALL | TAP | unknown_default_open_api>",
    "bidStrategyType": "<one of: MANUAL_CPT | MAX_CONVERSIONS | MANUAL_CPM | MAX_ENGAGEMENTS | unknown_default_open_api>"
  },
  "dailyBudget": {
    "value": {
      "amount": "<string>"
    }
  },
  "endTime": "<string>",
  "invoiceDetail": {
    "billingEmail": "<string>",
    "clientName": "<string>",
    "orderNumber": "<string>",
    "primaryBuyerEmail": "<string>",
    "primaryBuyerName": "<string>"
  },
  "name": "<string>",
  "regulationResponses": [
    {
      "regulationType": "<one of: CAC | CAMPAIGN_SAPIN_LAW | ORG_SAPIN_LAW | unknown_default_open_api>",
      "responseValue": "<one of: AGENT | FALSE | FRENCH_BUSINESS | NOT_AGENT | NOT_ANSWERED | NOT_FRENCH_BUSINESS | TRUE | unknown_default_open_api>"
    }
  ],
  "sharedBudgets": [
    {
      "budgetId": 0
    }
  ],
  "startTime": "<string>",
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>",
  "targeting": {
    "countryOrRegion": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "supplyPlacement": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "supplySource": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    }
  }
}
```

#### Referenced structures

##### `BidStrategyGoal`

BidStrategyGoal

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `BidStrategyType`

BidStrategyType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `BidStrategyUpdate`

BidStrategyUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `bid` | no | `Money | null` | `None` |  |
| `bidStrategyGoal` | no | `BidStrategyGoal | null` | `None` |  |
| `bidStrategyType` | no | `BidStrategyType | null` | `None` |  |

##### `CampaignStatus`

CampaignStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `CampaignTargetingUpdate`

CampaignTargetingUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `countryOrRegion` | no | `TargetingDataUpdate | null` | `None` |  |
| `supplyPlacement` | no | `TargetingDataUpdate | null` | `None` |  |
| `supplySource` | no | `TargetingDataUpdate | null` | `None` |  |

##### `DailyBudgetUpdate`

DailyBudgetUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `value` | no | `Money | null` | `None` |  |

##### `InvoiceDetailUpdate`

InvoiceDetailUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `billingEmail` | no | `string | null` | `None` |  |
| `clientName` | no | `string | null` | `None` |  |
| `orderNumber` | no | `string | null` | `None` |  |
| `primaryBuyerEmail` | no | `string | null` | `None` |  |
| `primaryBuyerName` | no | `string | null` | `None` |  |

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

##### `RegulationResponseUpdate`

RegulationResponseUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `regulationType` | no | `RegulationType | null` | `None` |  |
| `responseValue` | no | `RegulationResponseValue | null` | `None` |  |

##### `RegulationResponseValue`

RegulationResponseValue

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RegulationType`

RegulationType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `SharedBudgetAssignmentUpdate`

SharedBudgetAssignmentUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `budgetId` | no | `integer | null` | `None` |  |

##### `TargetingDataUpdate`

TargetingDataUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `exclude` | no | `array[string] | null` | `None` |  |
| `include` | no | `array[string] | null` | `None` |  |
