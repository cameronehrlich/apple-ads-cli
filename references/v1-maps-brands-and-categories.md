<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Maps brands and categories

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`get_brand`](#get-brand)
- [`query_brands`](#query-brands)
- [`get_category`](#get-category)
- [`query_categories`](#query-categories)

## `get_brand`

- Status: `implemented`
- Canonical command: `asa business-brands get`
- Usage: `Usage: asa business-brands get [OPTIONS]`
- SDK contract: `GET /business-brands/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id`
- Body parameters: `[]`
- Returns: `BrandResponse`
- CLI help: Get business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `query_brands`

- Status: `implemented`
- Canonical command: `asa business-brands query`
- Usage: `Usage: asa business-brands query [OPTIONS]`
- SDK contract: `POST /business-brands/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context, query_request`
- Body parameters: `[{"annotation":"Annotated[QueryRequest, Field(description='A query object to filter, sort, and paginate the results')]","container":"model","default":null,"model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":true,"wire_name":"body"}]`
- Returns: `BrandQueryResponse`
- CLI help: Query business brands.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
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

## `get_category`

- Status: `implemented`
- Canonical command: `asa business-categories get`
- Usage: `Usage: asa business-categories get [OPTIONS]`
- SDK contract: `GET /business-categories/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id`
- Body parameters: `[]`
- Returns: `BusinessCategoryResponse`
- CLI help: Get business categories.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `query_categories`

- Status: `implemented`
- Canonical command: `asa business-categories query`
- Usage: `Usage: asa business-categories query [OPTIONS]`
- SDK contract: `POST /business-categories/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context, query_request`
- Body parameters: `[{"annotation":"Annotated[QueryRequest, Field(description='A query object to filter, sort, and paginate the results')]","container":"model","default":null,"model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":true,"wire_name":"body"}]`
- Returns: `BusinessCategoryQueryResponse`
- CLI help: Query business categories.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
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
