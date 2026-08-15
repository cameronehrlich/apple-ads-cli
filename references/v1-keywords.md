<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Targeting keywords

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`keywords_bulk_create_post`](#keywords-bulk-create-post)
- [`keywords_bulk_update_post`](#keywords-bulk-update-post)
- [`keywords_post`](#keywords-post)
- [`keywords_id_delete`](#keywords-id-delete)
- [`keywords_id_get`](#keywords-id-get)
- [`keywords_query_post`](#keywords-query-post)
- [`keywords_id_put`](#keywords-id-put)

## `keywords_bulk_create_post`

- Status: `implemented`
- Canonical command: `asa keywords bulk-create`
- Usage: `Usage: asa keywords bulk-create [OPTIONS]`
- SDK contract: `POST /keywords/bulk-create`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[KeywordCreateBulkRequest]","container":"model","default":"None","model":"apple_ads_platform.models.keyword_create_bulk_request.KeywordCreateBulkRequest","name":"keyword_create_bulk_request","required":false,"wire_name":"body"}]`
- Returns: `KeywordCreateBulkResponse`
- CLI help: Bulk create keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.keyword_create_bulk_request.KeywordCreateBulkRequest`

KeywordCreateBulkRequest

- Schema SHA-256: `7735bf67de92fda2942f631addce9ece067310504249c70e9e9e7faef95f8b7e`
- Source SHA-256: `90e6892bcb5ff217d9570eeffb487450b1a3d8a03f8d1529f03cd1f56a23c593`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `allowPartialSuccess` | no | `boolean | null` | `None` |  |
| `items` | no | `array[KeywordCreateBulkRequestItem] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "allowPartialSuccess": false,
  "items": [
    {
      "correlationId": 0,
      "data": {
        "adGroupId": 0,
        "text": "<string>"
      }
    }
  ]
}
```

#### Referenced structures

##### `BulkKeywordCreate`

BulkKeywordCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adGroupId` | yes | `integer` | — |  |
| `bid` | no | `Money | null` | `None` |  |
| `matchType` | no | `KeywordMatchType | null` | `None` |  |
| `status` | no | `KeywordStatus | null` | `None` |  |
| `text` | yes | `string` | — |  |

##### `KeywordCreateBulkRequestItem`

KeywordCreateBulkRequestItem

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `correlationId` | no | `integer | null` | `None` |  |
| `data` | no | `BulkKeywordCreate | null` | `None` |  |

##### `KeywordMatchType`

KeywordMatchType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `KeywordStatus`

KeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

## `keywords_bulk_update_post`

- Status: `implemented`
- Canonical command: `asa keywords bulk-update`
- Usage: `Usage: asa keywords bulk-update [OPTIONS]`
- SDK contract: `POST /keywords/bulk-update`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[KeywordUpdateBulkRequest]","container":"model","default":"None","model":"apple_ads_platform.models.keyword_update_bulk_request.KeywordUpdateBulkRequest","name":"keyword_update_bulk_request","required":false,"wire_name":"body"}]`
- Returns: `KeywordUpdateBulkResponse`
- CLI help: Bulk update keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.keyword_update_bulk_request.KeywordUpdateBulkRequest`

KeywordUpdateBulkRequest

- Schema SHA-256: `9be68782c77db665a315751405dda22ae0eee87d075a70f92cb986a4b48a2fd7`
- Source SHA-256: `82d5ff49f6d9a751692edd31441b755ea96cd94d7d90db32ca71f6d785d96b1f`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `allowPartialSuccess` | no | `boolean | null` | `None` |  |
| `items` | no | `array[KeywordUpdateBulkRequestItem] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "allowPartialSuccess": false,
  "items": [
    {
      "correlationId": 0,
      "data": {
        "id": 0
      }
    }
  ]
}
```

#### Referenced structures

##### `BulkKeywordUpdate`

BulkKeywordUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `bid` | no | `Money | null` | `None` |  |
| `id` | yes | `integer` | — |  |
| `status` | no | `KeywordStatus | null` | `None` |  |

##### `KeywordStatus`

KeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `KeywordUpdateBulkRequestItem`

KeywordUpdateBulkRequestItem

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `correlationId` | no | `integer | null` | `None` |  |
| `data` | no | `BulkKeywordUpdate | null` | `None` |  |

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

## `keywords_post`

- Status: `implemented`
- Canonical command: `asa keywords create`
- Usage: `Usage: asa keywords create [OPTIONS]`
- SDK contract: `POST /keywords`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[KeywordCreate]","container":"model","default":"None","model":"apple_ads_platform.models.keyword_create.KeywordCreate","name":"keyword_create","required":false,"wire_name":"body"}]`
- Returns: `KeywordResponse`
- CLI help: Create keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.keyword_create.KeywordCreate`

KeywordCreate

- Schema SHA-256: `1bc06d660f546796e5e201655e0e9e172f09c6e0a0ceaf183271375eac179ee4`
- Source SHA-256: `d4fa958c68158fd53e2d320b015cde48e975de9607dba4509c2b6bab093a1a70`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adGroupId` | yes | `integer` | — |  |
| `bid` | no | `Money | null` | `None` |  |
| `matchType` | no | `KeywordMatchType | null` | `None` |  |
| `status` | no | `KeywordStatus | null` | `None` |  |
| `text` | yes | `string` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adGroupId": 0,
  "text": "<string>"
}
```

#### Referenced structures

##### `KeywordMatchType`

KeywordMatchType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `KeywordStatus`

KeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

## `keywords_id_delete`

- Status: `implemented`
- Canonical command: `asa keywords delete`
- Usage: `Usage: asa keywords delete [OPTIONS]`
- SDK contract: `DELETE /keywords/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `keywords_id_get`

- Status: `implemented`
- Canonical command: `asa keywords get`
- Usage: `Usage: asa keywords get [OPTIONS]`
- SDK contract: `GET /keywords/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `KeywordResponse`
- CLI help: Get keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `keywords_query_post`

- Status: `implemented`
- Canonical command: `asa keywords query`
- Usage: `Usage: asa keywords query [OPTIONS]`
- SDK contract: `POST /keywords/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `KeywordQueryResponse`
- CLI help: Query keywords.

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

## `keywords_id_put`

- Status: `implemented`
- Canonical command: `asa keywords update`
- Usage: `Usage: asa keywords update [OPTIONS]`
- SDK contract: `PUT /keywords/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[KeywordUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.keyword_update.KeywordUpdate","name":"keyword_update","required":false,"wire_name":"body"}]`
- Returns: `KeywordResponse`
- CLI help: Update keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.keyword_update.KeywordUpdate`

KeywordUpdate

- Schema SHA-256: `75a7844d9447c60b965fd948bd9aeadaf72c9ca05fbfa2d313b903b6ce79b578`
- Source SHA-256: `6f408601a61fb482f254be78e748401f4dba6b15aa05cf9b98aa85a5093c7d46`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `bid` | no | `Money | null` | `None` |  |
| `status` | no | `KeywordStatus | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "bid": {
    "amount": "<string>"
  },
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>"
}
```

#### Referenced structures

##### `KeywordStatus`

KeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |
