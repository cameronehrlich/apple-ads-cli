<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Maps locations and geo

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`get_geos_by_ids`](#get-geos-by-ids)
- [`search_geos`](#search-geos)
- [`create_location_group`](#create-location-group)
- [`delete_location_group`](#delete-location-group)
- [`get_location_group`](#get-location-group)
- [`query_location_groups`](#query-location-groups)
- [`update_location_group`](#update-location-group)
- [`get_location`](#get-location)
- [`query_locations`](#query-locations)

## `get_geos_by_ids`

- Status: `implemented`
- Canonical command: `asa geos get-by-ids`
- Usage: `Usage: asa geos get-by-ids [OPTIONS]`
- SDK contract: `POST /search/geo`
- Context: `required`
- Mutation: `no`
- Pagination: `geo-search-pagination`
- Required SDK parameters: `x_ap_context, geo_search_post_request`
- Body parameters: `[{"annotation":"Annotated[GeoSearchPostRequest, Field(description='Geo search request with entity criteria and pagination.')]","container":"model","default":null,"model":"apple_ads_platform.models.geo_search_post_request.GeoSearchPostRequest","name":"geo_search_post_request","required":true,"wire_name":"body"}]`
- Returns: `GeoSearchResponse`
- CLI help: Get by ids geos.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.geo_search_post_request.GeoSearchPostRequest`

GeoSearchPostRequest

- Schema SHA-256: `360197b1371b453de1b8b0413dbbc3c5d421d2b76a7cb9dbc63b1b5625e81efd`
- Source SHA-256: `112528304e7fdefdd198abe925fde3565915c7d9b9001d1286966cf0f2c70123`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `geoRequest` | yes | `array[GeoRequest]` | — | List of geo entity based search criteria. |
| `pagination` | no | `GeoSearchPagination | null` | `None` |  |
| `supplySource` | yes | `SearchSupplySourceType` | — | Supply source context. **Required.** Case-insensitive. |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "geoRequest": [
    {
      "entity": "<one of: Country | AdminArea | Locality | PostalCode | unknown_default_open_api>"
    }
  ],
  "supplySource": "<one of: APPSTORE | MAPS | unknown_default_open_api>"
}
```

#### Referenced structures

##### `GeoEntityType`

Geo entity type (a.k.a. dimension).

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `GeoRequest`

A single geo lookup request. Must have either `id` (numeric geo_location_id) or `legacyId` (pipe-delimited geo code), but not both.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `entity` | yes | `GeoEntityType` | — |  |
| `id` | no | `string | null` | `None` | Numeric geo location identifier (geo_location_id). Mutually exclusive with legacyId. |
| `legacyId` | no | `string | null` | `None` | Pipe-delimited geo code (e.g. "US\|CA\|San Francisco", "US\|TX\|78238"). Mutually exclusive with id. |

##### `GeoSearchPagination`

GeoSearchPagination

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `None` |  |
| `pageSize` | no | `integer | null` | `None` |  |
| `totalCount` | no | `integer | null` | `None` |  |

##### `SearchSupplySourceType`

Supply source context for geo search.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `search_geos`

- Status: `implemented`
- Canonical command: `asa geos search`
- Usage: `Usage: asa geos search [OPTIONS]`
- SDK contract: `GET /search/geo`
- Context: `required`
- Mutation: `no`
- Pagination: `offset-page-size`
- Required SDK parameters: `x_ap_context, supply_source`
- Body parameters: `[]`
- Returns: `GeoSearchResponse`
- CLI help: Search geos.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--countrycode` | no | `text` | — | — | countrycode parameter |
| option | `--eligible` | no | `boolean` | — | — | eligible parameter |
| option | `--entity` | no | `text` | — | — | entity parameter |
| option | `--offset` | no | `integer` | — | — | offset parameter |
| option | `--page-size` | no | `integer` | — | — | pageSize parameter |
| option | `--query` | no | `text` | — | — | query parameter |
| option | `--supply-source` | yes | `text` | — | — | supplySource parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `create_location_group`

- Status: `implemented`
- Canonical command: `asa location-groups create`
- Usage: `Usage: asa location-groups create [OPTIONS]`
- SDK contract: `POST /location-groups`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, location_group_create`
- Body parameters: `[{"annotation":"Annotated[LocationGroupCreate, Field(description='Location group details to create')]","container":"model","default":null,"model":"apple_ads_platform.models.location_group_create.LocationGroupCreate","name":"location_group_create","required":true,"wire_name":"body"}]`
- Returns: `LocationGroupResponse`
- CLI help: Create location groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.location_group_create.LocationGroupCreate`

LocationGroupCreate

- Schema SHA-256: `54d131702ade23f225ceb63d1efb12f41c36718fc502036b768df7b7affcf570`
- Source SHA-256: `e19f208f6e845733b35a0985d6700213cb5d1cc6d8dd7f0587f944b401daf3bc`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `adAccountId` | yes | `string` | — |  |
| `brandId` | yes | `string` | — |  |
| `description` | no | `string | null` | `None` |  |
| `groupType` | yes | `LocationGroupType` | — |  |
| `locationIds` | no | `array[string] | null` | `None` | Location identifiers for STATIC type |
| `name` | yes | `string` | — |  |
| `rules` | no | `array[Rule] | null` | `None` | Structured rules for DYNAMIC groups. Use instead of raw `query`. Supported fields: adminArea, locality, postalCode, locationId. Operators: EQUALS, NOT_EQUALS, IN, NOT_IN. Use `value` for all operators (string for EQUALS/NOT_EQUALS, array for IN/NOT_IN). |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "adAccountId": "<string>",
  "brandId": "<string>",
  "groupType": "<one of: DYNAMIC | STATIC | unknown_default_open_api>",
  "name": "<string>"
}
```

#### Referenced structures

##### `LocationGroupType`

How a LocationGroup is composed. DYNAMIC groups select members via rules; STATIC groups have a fixed, explicitly-enumerated member list.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `Rule`

A single filter rule for DYNAMIC location groups. Use `value` (string) for EQUALS/NOT_EQUALS. Use `value` (array) for IN/NOT_IN.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — |  |
| `operator` | yes | `string` | — |  |
| `value` | yes | `any | null` | — | Single value string (for EQUALS/NOT_EQUALS) or array of string value (for IN/NOT_IN) |

## `delete_location_group`

- Status: `implemented`
- Canonical command: `asa location-groups delete`
- Usage: `Usage: asa location-groups delete [OPTIONS]`
- SDK contract: `DELETE /location-groups/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id`
- Body parameters: `[]`
- Returns: `LocationGroupResponse`
- CLI help: Delete location groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `get_location_group`

- Status: `implemented`
- Canonical command: `asa location-groups get`
- Usage: `Usage: asa location-groups get [OPTIONS]`
- SDK contract: `GET /location-groups/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id`
- Body parameters: `[]`
- Returns: `LocationGroupResponse`
- CLI help: Get location groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `query_location_groups`

- Status: `implemented`
- Canonical command: `asa location-groups query`
- Usage: `Usage: asa location-groups query [OPTIONS]`
- SDK contract: `POST /location-groups/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context, query_request`
- Body parameters: `[{"annotation":"Annotated[QueryRequest, Field(description='A query object to filter, sort, and paginate the results')]","container":"model","default":null,"model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":true,"wire_name":"body"}]`
- Returns: `LocationGroupQueryResponse`
- CLI help: Query location groups.

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

## `update_location_group`

- Status: `implemented`
- Canonical command: `asa location-groups update`
- Usage: `Usage: asa location-groups update [OPTIONS]`
- SDK contract: `PUT /location-groups/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id, location_group_update`
- Body parameters: `[{"annotation":"Annotated[LocationGroupUpdate, Field(description='Updated location group details')]","container":"model","default":null,"model":"apple_ads_platform.models.location_group_update.LocationGroupUpdate","name":"location_group_update","required":true,"wire_name":"body"}]`
- Returns: `LocationGroupResponse`
- CLI help: Update location groups.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.location_group_update.LocationGroupUpdate`

LocationGroupUpdate

- Schema SHA-256: `44a52d4141d3b3823d032b70356cf005a4c682b86213704af502ac1c13f803a5`
- Source SHA-256: `da216cbf0209d3462efd5033ed7e7a8740040296903cd0bd87b7962753939b1f`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `description` | no | `string | null` | `None` |  |
| `groupType` | no | `LocationGroupType | null` | `None` |  |
| `locationIds` | no | `array[string] | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |
| `rules` | no | `array[Rule] | null` | `None` | Structured rules for DYNAMIC groups. Changing rules sets systemStatus to PENDING. Use `value` for all operators (string for EQUALS/NOT_EQUALS, array for IN/NOT_IN). |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "description": "<string>",
  "groupType": "<one of: DYNAMIC | STATIC | unknown_default_open_api>",
  "locationIds": [
    "<string>"
  ],
  "name": "<string>",
  "rules": [
    {
      "field": "<string>",
      "operator": "<string>",
      "value": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `LocationGroupType`

How a LocationGroup is composed. DYNAMIC groups select members via rules; STATIC groups have a fixed, explicitly-enumerated member list.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `Rule`

A single filter rule for DYNAMIC location groups. Use `value` (string) for EQUALS/NOT_EQUALS. Use `value` (array) for IN/NOT_IN.

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — |  |
| `operator` | yes | `string` | — |  |
| `value` | yes | `any | null` | — | Single value string (for EQUALS/NOT_EQUALS) or array of string value (for IN/NOT_IN) |

## `get_location`

- Status: `implemented`
- Canonical command: `asa locations get`
- Usage: `Usage: asa locations get [OPTIONS]`
- SDK contract: `GET /locations/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, id`
- Body parameters: `[]`
- Returns: `LocationResponse`
- CLI help: Get locations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `query_locations`

- Status: `implemented`
- Canonical command: `asa locations query`
- Usage: `Usage: asa locations query [OPTIONS]`
- SDK contract: `POST /locations/query`
- Context: `required`
- Mutation: `no`
- Pagination: `query-pagination`
- Required SDK parameters: `x_ap_context, query_request`
- Body parameters: `[{"annotation":"Annotated[QueryRequest, Field(description='A query object to filter, sort, and paginate the results')]","container":"model","default":null,"model":"apple_ads_platform.models.query_request.QueryRequest","name":"query_request","required":true,"wire_name":"body"}]`
- Returns: `LocationQueryResponse`
- CLI help: Query locations.

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
