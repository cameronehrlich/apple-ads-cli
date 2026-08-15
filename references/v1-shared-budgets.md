<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Shared budgets

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`shared_budgets_post`](#shared-budgets-post)
- [`shared_budgets_id_delete`](#shared-budgets-id-delete)
- [`shared_budgets_id_get`](#shared-budgets-id-get)
- [`shared_budgets_query_post`](#shared-budgets-query-post)
- [`shared_budgets_id_put`](#shared-budgets-id-put)

## `shared_budgets_post`

- Status: `implemented`
- Canonical command: `asa shared-budgets create`
- Usage: `Usage: asa shared-budgets create [OPTIONS]`
- SDK contract: `POST /shared-budgets`
- Context: `none`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `none`
- Body parameters: `[{"annotation":"Optional[SharedBudgetCreate]","container":"model","default":"None","model":"apple_ads_platform.models.shared_budget_create.SharedBudgetCreate","name":"shared_budget_create","required":false,"wire_name":"body"}]`
- Returns: `SharedBudgetResponse`
- CLI help: Create shared budgets.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.shared_budget_create.SharedBudgetCreate`

SharedBudgetCreate

- Schema SHA-256: `9ccabe2d82adb53e9fd29fbe9008dd9854f205dc664d9bd6a7390e3a20570318`
- Source SHA-256: `d1fe81ebc203dbbf8ccf2e8483f2ed14557232d2eda193e41ff6b83b6e801239`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adAccountIds` | yes | `array[integer]` | — |  |
| `endTime` | no | `string | null` | `None` |  |
| `invoiceDetail` | yes | `InvoiceDetailCreate` | — |  |
| `name` | yes | `string` | — |  |
| `startTime` | yes | `string` | — |  |
| `value` | yes | `Money` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adAccountIds": [
    0
  ],
  "invoiceDetail": {
    "billingEmail": "<string>",
    "primaryBuyerEmail": "<string>",
    "primaryBuyerName": "<string>"
  },
  "name": "<string>",
  "startTime": "<string>",
  "value": {
    "amount": "<string>"
  }
}
```

#### Referenced structures

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

## `shared_budgets_id_delete`

- Status: `implemented`
- Canonical command: `asa shared-budgets delete`
- Usage: `Usage: asa shared-budgets delete [OPTIONS]`
- SDK contract: `DELETE /shared-budgets/{id}`
- Context: `none`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete shared budgets.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `shared_budgets_id_get`

- Status: `implemented`
- Canonical command: `asa shared-budgets get`
- Usage: `Usage: asa shared-budgets get [OPTIONS]`
- SDK contract: `GET /shared-budgets/{id}`
- Context: `optional`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id`
- Body parameters: `[]`
- Returns: `SharedBudgetResponse`
- CLI help: Get shared budgets.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `shared_budgets_query_post`

- Status: `implemented`
- Canonical command: `asa shared-budgets query`
- Usage: `Usage: asa shared-budgets query [OPTIONS]`
- SDK contract: `POST /shared-budgets/query`
- Context: `optional`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `none`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `SharedBudgetQueryResponse`
- CLI help: Query shared budgets.

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

## `shared_budgets_id_put`

- Status: `implemented`
- Canonical command: `asa shared-budgets update`
- Usage: `Usage: asa shared-budgets update [OPTIONS]`
- SDK contract: `PUT /shared-budgets/{id}`
- Context: `none`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id`
- Body parameters: `[{"annotation":"Optional[SharedBudgetUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.shared_budget_update.SharedBudgetUpdate","name":"shared_budget_update","required":false,"wire_name":"body"}]`
- Returns: `SharedBudgetResponse`
- CLI help: Update shared budgets.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.shared_budget_update.SharedBudgetUpdate`

SharedBudgetUpdate

- Schema SHA-256: `49cb35e024ea892bde5457d7721298d09c1758878939a4a6eb91229e11b46ccd`
- Source SHA-256: `80ad77cf60518a659e3d09ca9388081bf796be278b790bafddca96e90d07529c`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adAccountIds` | no | `array[integer] | null` | `None` |  |
| `endTime` | no | `string | null` | `None` |  |
| `invoiceDetail` | no | `InvoiceDetailUpdate | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |
| `startTime` | no | `string | null` | `None` |  |
| `value` | no | `Money | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adAccountIds": [
    0
  ],
  "endTime": "<string>",
  "invoiceDetail": {
    "billingEmail": "<string>",
    "clientName": "<string>",
    "orderNumber": "<string>",
    "primaryBuyerEmail": "<string>",
    "primaryBuyerName": "<string>"
  },
  "name": "<string>",
  "startTime": "<string>",
  "value": {
    "amount": "<string>"
  }
}
```

#### Referenced structures

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
