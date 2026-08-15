<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Ad groups

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`adgroups_post`](#adgroups-post)
- [`adgroups_id_delete`](#adgroups-id-delete)
- [`adgroups_id_get`](#adgroups-id-get)
- [`adgroups_query_post`](#adgroups-query-post)
- [`adgroups_id_put`](#adgroups-id-put)

## `adgroups_post`

- Status: `implemented`
- Canonical command: `asa ad-groups create`
- Usage: `Usage: asa ad-groups create [OPTIONS]`
- SDK contract: `POST /adgroups`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[AdGroupCreate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_group_create.AdGroupCreate","name":"ad_group_create","required":false,"wire_name":"body"}]`
- Returns: `AdGroupResponse`
- CLI help: Create ad groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_group_create.AdGroupCreate`

AdGroupCreate

- Schema SHA-256: `500c4160d61a9f6890099428aada8f6bd5c5e5ae2ae27e30a3ac1c9a87de785b`
- Source SHA-256: `9e6d0374ad9b9a596e92e43aff0146832f58e47a14120aac8df4a81720a9b076`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `automatedKeywordsOptIn` | no | `boolean | null` | `None` |  |
| `automatedKeywordsRequired` | no | `boolean | null` | `None` |  |
| `bidStrategy` | no | `BidStrategyCreate | null` | `None` |  |
| `campaignId` | yes | `integer` | — |  |
| `cpaCap` | no | `CPAGoalCreate | null` | `None` | Use Max Conversion bid strategy. See BidStrategy. |
| `endTime` | no | `string | null` | `None` |  |
| `name` | yes | `string` | — |  |
| `pricingModel` | yes | `PricingModel` | — |  |
| `startTime` | no | `string | null` | `None` |  |
| `status` | no | `AdGroupStatus | null` | `None` |  |
| `targeting` | no | `AdGroupTargetingCreate | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "campaignId": 0,
  "name": "<string>",
  "pricingModel": "<one of: CPA | CPM | CPT | unknown_default_open_api>"
}
```

#### Referenced structures

##### `AdGroupStatus`

AdGroupStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `AdGroupTargetingCreate`

AdGroupTargetingCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adminArea` | no | `TargetingDataCreate | null` | `None` |  |
| `appCategory` | no | `TargetingDataCreate | null` | `None` |  |
| `appDownloader` | no | `TargetingDataCreate | null` | `None` |  |
| `country` | no | `TargetingDataCreate | null` | `None` |  |
| `daypart` | no | `TargetingDataCreate | null` | `None` |  |
| `deviceClass` | no | `TargetingDataCreate | null` | `None` |  |
| `gender` | no | `TargetingDataCreate | null` | `None` |  |
| `locality` | no | `TargetingDataCreate | null` | `None` |  |
| `locationGroup` | no | `TargetingDataCreate | null` | `None` |  |
| `maxAge` | no | `TargetingDataCreate | null` | `None` |  |
| `minAge` | no | `TargetingDataCreate | null` | `None` |  |
| `postalCode` | no | `TargetingDataCreate | null` | `None` |  |
| `radius` | no | `TargetingDataCreate | null` | `None` |  |
| `travelIntent` | no | `TargetingDataCreate | null` | `None` |  |

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

##### `CPAGoalCreate`

CPAGoalCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `value` | no | `Money | null` | `None` |  |

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

##### `PricingModel`

PricingModel

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `TargetingDataCreate`

TargetingDataCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `exclude` | no | `array[string] | null` | `None` |  |
| `include` | no | `array[string] | null` | `None` |  |

## `adgroups_id_delete`

- Status: `implemented`
- Canonical command: `asa ad-groups delete`
- Usage: `Usage: asa ad-groups delete [OPTIONS]`
- SDK contract: `DELETE /adgroups/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `Response`
- CLI help: Delete ad groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `adgroups_id_get`

- Status: `implemented`
- Canonical command: `asa ad-groups get`
- Usage: `Usage: asa ad-groups get [OPTIONS]`
- SDK contract: `GET /adgroups/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `AdGroupResponse`
- CLI help: Get ad groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `adgroups_query_post`

- Status: `implemented`
- Canonical command: `asa ad-groups query`
- Usage: `Usage: asa ad-groups query [OPTIONS]`
- SDK contract: `POST /adgroups/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context`
- Body parameters: `[{"annotation":"Optional[QueryRequest]","container":"model","default":"None","model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":false,"wire_name":"body"}]`
- Returns: `AdGroupQueryResponse`
- CLI help: Query ad groups.

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

## `adgroups_id_put`

- Status: `implemented`
- Canonical command: `asa ad-groups update`
- Usage: `Usage: asa ad-groups update [OPTIONS]`
- SDK contract: `PUT /adgroups/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[AdGroupUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_group_update.AdGroupUpdate","name":"ad_group_update","required":false,"wire_name":"body"}]`
- Returns: `AdGroupResponse`
- CLI help: Update ad groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_group_update.AdGroupUpdate`

AdGroupUpdate

- Schema SHA-256: `57a3bce2364b2d23f6e30106b33edbd836efda0ee14f0b26cd34bd69907486ec`
- Source SHA-256: `4ff8464bfd690d4d0487745b7132483a4616b9a4b4a0360f17bf7cf1d22e67fc`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `automatedKeywordsOptIn` | no | `boolean | null` | `None` |  |
| `automatedKeywordsRequired` | no | `boolean | null` | `None` |  |
| `bidStrategy` | no | `BidStrategyUpdate | null` | `None` |  |
| `cpaCap` | no | `CPAGoalUpdate | null` | `None` | Use Max Conversion bid strategy. See BidStrategy. |
| `endTime` | no | `string | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |
| `startTime` | no | `string | null` | `None` |  |
| `status` | no | `AdGroupStatus | null` | `None` |  |
| `targeting` | no | `AdGroupTargetingUpdate | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "automatedKeywordsOptIn": false,
  "automatedKeywordsRequired": false,
  "bidStrategy": {
    "bid": {
      "amount": "<string>"
    },
    "bidStrategyGoal": "<one of: IMPRESSION | INSTALL | TAP | unknown_default_open_api>",
    "bidStrategyType": "<one of: MANUAL_CPT | MAX_CONVERSIONS | MANUAL_CPM | MAX_ENGAGEMENTS | unknown_default_open_api>"
  },
  "cpaCap": {
    "value": {
      "amount": "<string>"
    }
  },
  "endTime": "<string>",
  "name": "<string>",
  "startTime": "<string>",
  "status": "<one of: ENABLED | PAUSED | unknown_default_open_api>",
  "targeting": {
    "adminArea": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "appCategory": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "appDownloader": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "country": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "daypart": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "deviceClass": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "gender": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "locality": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "locationGroup": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "maxAge": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "minAge": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "postalCode": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "radius": {
      "exclude": [
        "<string>"
      ],
      "include": [
        "<string>"
      ]
    },
    "travelIntent": {
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

##### `AdGroupStatus`

AdGroupStatus

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `AdGroupTargetingUpdate`

AdGroupTargetingUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adminArea` | no | `TargetingDataUpdate | null` | `None` |  |
| `appCategory` | no | `TargetingDataUpdate | null` | `None` |  |
| `appDownloader` | no | `TargetingDataUpdate | null` | `None` |  |
| `country` | no | `TargetingDataUpdate | null` | `None` |  |
| `daypart` | no | `TargetingDataUpdate | null` | `None` |  |
| `deviceClass` | no | `TargetingDataUpdate | null` | `None` |  |
| `gender` | no | `TargetingDataUpdate | null` | `None` |  |
| `locality` | no | `TargetingDataUpdate | null` | `None` |  |
| `locationGroup` | no | `TargetingDataUpdate | null` | `None` |  |
| `maxAge` | no | `TargetingDataUpdate | null` | `None` |  |
| `minAge` | no | `TargetingDataUpdate | null` | `None` |  |
| `postalCode` | no | `TargetingDataUpdate | null` | `None` |  |
| `radius` | no | `TargetingDataUpdate | null` | `None` |  |
| `travelIntent` | no | `TargetingDataUpdate | null` | `None` |  |

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

##### `CPAGoalUpdate`

CPAGoalUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `value` | no | `Money | null` | `None` |  |

##### `Money`

Money

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | The monetary value in the specified currency. The API uses amount whenever a currency value is necessary. The string can contain up to two decimal digits. |
| `currency` | no | `string | null` | `None` | The organization’s default currency that is set up in the Apple Search Ads UI. |

##### `TargetingDataUpdate`

TargetingDataUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `exclude` | no | `array[string] | null` | `None` |  |
| `include` | no | `array[string] | null` | `None` |  |
