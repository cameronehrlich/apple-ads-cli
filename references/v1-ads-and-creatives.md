<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Ads and creatives

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`ads_post`](#ads-post)
- [`ads_id_delete`](#ads-id-delete)
- [`ads_id_get`](#ads-id-get)
- [`ads_query_post`](#ads-query-post)
- [`ads_id_put`](#ads-id-put)
- [`creatives_post`](#creatives-post)
- [`creatives_id_delete`](#creatives-id-delete)
- [`creatives_id_get`](#creatives-id-get)
- [`creatives_query_post`](#creatives-query-post)
- [`creatives_id_put`](#creatives-id-put)
- [`rejection_reasons_apps_rejection_reason_id_get`](#rejection-reasons-apps-rejection-reason-id-get)
- [`rejection_reasons_apps_query_post`](#rejection-reasons-apps-query-post)
- [`query_rejection_reasons_by_business_brand`](#query-rejection-reasons-by-business-brand)

## `ads_post`

- Status: `implemented`
- Canonical command: `asa ads create`
- Usage: `Usage: asa ads create [OPTIONS]`
- SDK contract: `POST /ads`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[AdCreate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_create.AdCreate","name":"ad_create","required":false,"wire_name":"body"}]`
- Returns: `AdResponse`
- CLI help: Create ads.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_create.AdCreate`

AdCreate

- Schema SHA-256: `8b45f88709c8a0afc39484c27f481cb61a9cbc8b24eb2ac2c1d27479e38a886b`
- Source SHA-256: `311a12ca285de91328bfc3a75510cad95c36d64638b07a408f39678a59a90030`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adGroupId` | yes | `integer` | — |  |
| `creativeId` | yes | `integer` | — |  |
| `name` | yes | `string` | — |  |
| `status` | yes | `AdStatus` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adGroupId": 0,
  "creativeId": 0,
  "name": "<string>",
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>"
}
```

#### Referenced structures

##### `AdStatus`

AdStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `ads_id_delete`

- Status: `implemented`
- Canonical command: `asa ads delete`
- Usage: `Usage: asa ads delete [OPTIONS]`
- SDK contract: `DELETE /ads/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete ads.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `ads_id_get`

- Status: `implemented`
- Canonical command: `asa ads get`
- Usage: `Usage: asa ads get [OPTIONS]`
- SDK contract: `GET /ads/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `AdResponse`
- CLI help: Get ads.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `ads_query_post`

- Status: `implemented`
- Canonical command: `asa ads query`
- Usage: `Usage: asa ads query [OPTIONS]`
- SDK contract: `POST /ads/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `AdQueryResponse`
- CLI help: Query ads.

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

## `ads_id_put`

- Status: `implemented`
- Canonical command: `asa ads update`
- Usage: `Usage: asa ads update [OPTIONS]`
- SDK contract: `PUT /ads/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[AdUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_update.AdUpdate","name":"ad_update","required":false,"wire_name":"body"}]`
- Returns: `AdResponse`
- CLI help: Update ads.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_update.AdUpdate`

AdUpdate

- Schema SHA-256: `c0b67f2d8d468bc320e7b327823b7075f916fd116dc3d6f6e957f5174fc0416c`
- Source SHA-256: `11bd9f49a2003a70b7acfb08dabfbdbfbe282414f4eee7bd6c92e08157e575e1`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `name` | no | `string | null` | `None` |  |
| `status` | no | `AdStatus | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "name": "<string>",
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>"
}
```

#### Referenced structures

##### `AdStatus`

AdStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `creatives_post`

- Status: `implemented`
- Canonical command: `asa creatives create`
- Usage: `Usage: asa creatives create [OPTIONS]`
- SDK contract: `POST /creatives`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[CreativeCreate]","container":"model","default":"None","model":"apple_ads_platform.models.creative_create.CreativeCreate","name":"creative_create","required":false,"wire_name":"body"}]`
- Returns: `CreativeResponse`
- CLI help: Create creatives.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.creative_create.CreativeCreate`

CreativeCreate

- Schema SHA-256: `2b39b6b2cf7239c7313dbcc760e5ab3babead8e15d51a26dc47e34e5d82ad705`
- Source SHA-256: `1c9feac7f4e6dfec5d0b4c72cb211e9a3008578d4883cc67ba2d8b819ef97c17`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `creativeSpec` | no | `object | null` | `None` |  |
| `creativeType` | yes | `CreativeType` | — |  |
| `destination` | yes | `DestinationCreate` | — |  |
| `name` | yes | `string` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "creativeType": "<one of: CUSTOM_PRODUCT_PAGE | DEFAULT_PRODUCT_PAGE | LOCAL_ADS_SEARCH_CREATIVE | unknown_default_open_api>",
  "destination": {
    "destinationType": "<one of: APP_STORE_PRODUCT_PAGE | LOCAL_ADS_PLACECARD | unknown_default_open_api>"
  },
  "name": "<string>"
}
```

#### Referenced structures

##### `CreativeType`

CreativeType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `DestinationCreate`

DestinationCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `destinationType` | yes | `DestinationType` | — |  |
| `parameters` | no | `DestinationParameter | null` | `None` |  |

##### `DestinationParameter`

DestinationParameter

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adamId` | no | `string | null` | `None` |  |
| `productPageId` | no | `string | null` | `None` |  |

##### `DestinationType`

DestinationType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `creatives_id_delete`

- Status: `implemented`
- Canonical command: `asa creatives delete`
- Usage: `Usage: asa creatives delete [OPTIONS]`
- SDK contract: `DELETE /creatives/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete creatives.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `creatives_id_get`

- Status: `implemented`
- Canonical command: `asa creatives get`
- Usage: `Usage: asa creatives get [OPTIONS]`
- SDK contract: `GET /creatives/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `CreativeResponse`
- CLI help: Get creatives.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `creatives_query_post`

- Status: `implemented`
- Canonical command: `asa creatives query`
- Usage: `Usage: asa creatives query [OPTIONS]`
- SDK contract: `POST /creatives/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `CreativeQueryResponse`
- CLI help: Query creatives.

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

## `creatives_id_put`

- Status: `implemented`
- Canonical command: `asa creatives update`
- Usage: `Usage: asa creatives update [OPTIONS]`
- SDK contract: `PUT /creatives/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[CreativeUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.creative_update.CreativeUpdate","name":"creative_update","required":false,"wire_name":"body"}]`
- Returns: `CreativeResponse`
- CLI help: Update creatives.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.creative_update.CreativeUpdate`

CreativeUpdate

- Schema SHA-256: `33c79f283c919142396e5b666c72af988ae794b96f2df9a3b5b5b2d6bc310bdf`
- Source SHA-256: `7705d38f2e7ec770fb1e4a0ddce202de7d86e61165925bf76c376c8cbb621c09`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `creativeSpec` | no | `object | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "creativeSpec": {},
  "name": "<string>"
}
```

## `rejection_reasons_apps_rejection_reason_id_get`

- Status: `implemented`
- Canonical command: `asa rejection-reasons get-app`
- Usage: `Usage: asa rejection-reasons get-app [OPTIONS]`
- SDK contract: `GET /rejection-reasons/apps/{rejectionReasonId}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, rejection_reason_id`
- Body parameters: `[]`
- Returns: `RejectionReasonResponse`
- CLI help: Get app rejection reasons.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--rejection-reason-id` | yes | `integer` | — | — | rejectionReasonId parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `rejection_reasons_apps_query_post`

- Status: `implemented`
- Canonical command: `asa rejection-reasons query-apps`
- Usage: `Usage: asa rejection-reasons query-apps [OPTIONS]`
- SDK contract: `POST /rejection-reasons/apps/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[CreativeRejectionReasonQueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.creative_rejection_reason_query_request.CreativeRejectionReasonQueryRequest","name":"creative_rejection_reason_query_request","required":false,"wire_name":"body"}]`
- Returns: `CreativeRejectionReasonQueryResponse`
- CLI help: Query apps rejection reasons.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.creative_rejection_reason_query_request.CreativeRejectionReasonQueryRequest`

CreativeRejectionReasonQueryRequest

- Schema SHA-256: `3c63b7377d910d7d273e0e2c260c9521e5295e5d639d5fbcbdb1079f6b8268cd`
- Source SHA-256: `67b0bc8f8a5980545da438b193170c4d210124c42055dcbaf53c81aeb266dc40`

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

## `query_rejection_reasons_by_business_brand`

- Status: `implemented`
- Canonical command: `asa rejection-reasons query-business-brands`
- Usage: `Usage: asa rejection-reasons query-business-brands [OPTIONS]`
- SDK contract: `POST /rejection-reasons/business-brands/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[PolicyAssignmentQueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.policy_assignment_query_request.PolicyAssignmentQueryRequest","name":"policy_assignment_query_request","required":false,"wire_name":"body"}]`
- Returns: `PolicyAssignmentQueryResponse`
- CLI help: Query business brands rejection reasons.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.policy_assignment_query_request.PolicyAssignmentQueryRequest`

PolicyAssignmentQueryRequest

- Schema SHA-256: `312d9271cdc8cad12998d921355c6c8dfad4bf4556b97d1b329c88f54de3a515`
- Source SHA-256: `0852071dfd7ccc3719a1c41aff7b7c22c746f2f7f627cadf8841c54dd4912803`

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
