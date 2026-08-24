<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Negative keywords

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`negative_keywords_bulk_create_post`](#negative-keywords-bulk-create-post)
- [`negative_keywords_bulk_update_post`](#negative-keywords-bulk-update-post)
- [`negative_keywords_post`](#negative-keywords-post)
- [`negative_keywords_id_delete`](#negative-keywords-id-delete)
- [`negative_keywords_id_get`](#negative-keywords-id-get)
- [`negative_keywords_query_post`](#negative-keywords-query-post)
- [`negative_keywords_id_put`](#negative-keywords-id-put)

## `negative_keywords_bulk_create_post`

- Status: `implemented`
- Canonical command: `asa negative-keywords bulk-create`
- Usage: `Usage: asa negative-keywords bulk-create [OPTIONS]`
- SDK contract: `POST /negative-keywords/bulk-create`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[NegativeKeywordCreateBulkRequest]","container":"model","default":"None","model":"apple_ads_platform.models.negative_keyword_create_bulk_request.NegativeKeywordCreateBulkRequest","name":"negative_keyword_create_bulk_request","required":false,"wire_name":"body"}]`
- Returns: `NegativeKeywordCreateBulkResponse`
- CLI help: Bulk create negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.negative_keyword_create_bulk_request.NegativeKeywordCreateBulkRequest`

NegativeKeywordCreateBulkRequest

- Schema SHA-256: `94bce3cb39bf17f83145c84e53a20c14a61134a1c6aa20d651a6a9bd2e608128`
- Source SHA-256: `98c9c30e457b3e60f6c9803b816775164c8403c6af777b0a3f5eba4a59c0ed1c`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `allowPartialSuccess` | no | `boolean | null` | `None` |  |
| `items` | no | `array[NegativeKeywordCreateBulkRequestItem] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "allowPartialSuccess": false,
  "items": [
    {
      "correlationId": 0,
      "data": {
        "text": "<string>"
      }
    }
  ]
}
```

#### Referenced structures

##### `BulkNegativeKeywordCreate`

BulkNegativeKeywordCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adGroupId` | no | `integer | null` | `None` |  |
| `campaignId` | no | `integer | null` | `None` |  |
| `matchType` | no | `KeywordMatchType | null` | `None` |  |
| `status` | no | `NegativeKeywordStatus | null` | `None` |  |
| `text` | yes | `string` | — |  |

##### `KeywordMatchType`

KeywordMatchType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `NegativeKeywordCreateBulkRequestItem`

NegativeKeywordCreateBulkRequestItem

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `correlationId` | no | `integer | null` | `None` |  |
| `data` | no | `BulkNegativeKeywordCreate | null` | `None` |  |

##### `NegativeKeywordStatus`

NegativeKeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `negative_keywords_bulk_update_post`

- Status: `implemented`
- Canonical command: `asa negative-keywords bulk-update`
- Usage: `Usage: asa negative-keywords bulk-update [OPTIONS]`
- SDK contract: `POST /negative-keywords/bulk-update`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[NegativeKeywordUpdateBulkRequest]","container":"model","default":"None","model":"apple_ads_platform.models.negative_keyword_update_bulk_request.NegativeKeywordUpdateBulkRequest","name":"negative_keyword_update_bulk_request","required":false,"wire_name":"body"}]`
- Returns: `NegativeKeywordUpdateBulkResponse`
- CLI help: Bulk update negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.negative_keyword_update_bulk_request.NegativeKeywordUpdateBulkRequest`

NegativeKeywordUpdateBulkRequest

- Schema SHA-256: `0218e5b4e35506e1b85a49be153d325e4669fc7cbd05b836803cac95b9dc5302`
- Source SHA-256: `c49758f2a043937031fc82a03af9967104e034c8798208db8d27746a5c3eba0c`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `allowPartialSuccess` | no | `boolean | null` | `None` |  |
| `items` | no | `array[NegativeKeywordUpdateBulkRequestItem] | null` | `None` |  |

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

##### `BulkNegativeKeywordUpdate`

BulkNegativeKeywordUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `id` | yes | `integer` | — |  |
| `status` | no | `NegativeKeywordStatus | null` | `None` |  |

##### `NegativeKeywordStatus`

NegativeKeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `NegativeKeywordUpdateBulkRequestItem`

NegativeKeywordUpdateBulkRequestItem

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `correlationId` | no | `integer | null` | `None` |  |
| `data` | no | `BulkNegativeKeywordUpdate | null` | `None` |  |

## `negative_keywords_post`

- Status: `implemented`
- Canonical command: `asa negative-keywords create`
- Usage: `Usage: asa negative-keywords create [OPTIONS]`
- SDK contract: `POST /negative-keywords`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[NegativeKeywordCreate]","container":"model","default":"None","model":"apple_ads_platform.models.negative_keyword_create.NegativeKeywordCreate","name":"negative_keyword_create","required":false,"wire_name":"body"}]`
- Returns: `NegativeKeywordResponse`
- CLI help: Create negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.negative_keyword_create.NegativeKeywordCreate`

NegativeKeywordCreate

- Schema SHA-256: `2eee312906b77dbcf5c0224cdee612c16476019a9f40f1e6acaa25318dba502f`
- Source SHA-256: `8017561910ab374006d24d6b7898cf995dbf8a6684c175fc2ad78e84f6ca5647`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adGroupId` | no | `integer | null` | `None` |  |
| `campaignId` | no | `integer | null` | `None` |  |
| `matchType` | no | `KeywordMatchType | null` | `None` |  |
| `status` | no | `NegativeKeywordStatus | null` | `None` |  |
| `text` | yes | `string` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "text": "<string>"
}
```

#### Referenced structures

##### `KeywordMatchType`

KeywordMatchType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `NegativeKeywordStatus`

NegativeKeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `negative_keywords_id_delete`

- Status: `implemented`
- Canonical command: `asa negative-keywords delete`
- Usage: `Usage: asa negative-keywords delete [OPTIONS]`
- SDK contract: `DELETE /negative-keywords/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `negative_keywords_id_get`

- Status: `implemented`
- Canonical command: `asa negative-keywords get`
- Usage: `Usage: asa negative-keywords get [OPTIONS]`
- SDK contract: `GET /negative-keywords/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `NegativeKeywordResponse`
- CLI help: Get negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `negative_keywords_query_post`

- Status: `implemented`
- Canonical command: `asa negative-keywords query`
- Usage: `Usage: asa negative-keywords query [OPTIONS]`
- SDK contract: `POST /negative-keywords/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `NegativeKeywordQueryResponse`
- CLI help: Query negative keywords.

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

## `negative_keywords_id_put`

- Status: `implemented`
- Canonical command: `asa negative-keywords update`
- Usage: `Usage: asa negative-keywords update [OPTIONS]`
- SDK contract: `PUT /negative-keywords/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[NegativeKeywordUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.negative_keyword_update.NegativeKeywordUpdate","name":"negative_keyword_update","required":false,"wire_name":"body"}]`
- Returns: `NegativeKeywordResponse`
- CLI help: Update negative keywords.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.negative_keyword_update.NegativeKeywordUpdate`

NegativeKeywordUpdate

- Schema SHA-256: `7b6427740dac46613fdf9ae81bf96dd8bc53d902287e15320091420cb8f2d776`
- Source SHA-256: `3b17b8da99a6c98a1a8843aa1bd654e47eb91fa303fbe56cb8b22723f91ae7a2`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `status` | no | `NegativeKeywordStatus | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>"
}
```

#### Referenced structures

##### `NegativeKeywordStatus`

NegativeKeywordStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
