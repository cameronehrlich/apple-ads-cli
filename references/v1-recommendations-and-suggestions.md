<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Recommendations and suggestions

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`apply_daily_budget_recommendations`](#apply-daily-budget-recommendations)
- [`dismiss_daily_budget_recommendations`](#dismiss-daily-budget-recommendations)
- [`query_daily_budget_recommendations`](#query-daily-budget-recommendations)
- [`apply_target_cpa_recommendations`](#apply-target-cpa-recommendations)
- [`dismiss_target_cpa_recommendations`](#dismiss-target-cpa-recommendations)
- [`query_target_cpa_recommendations`](#query-target-cpa-recommendations)
- [`query_category_suggestions`](#query-category-suggestions)
- [`query_keyword_suggestions`](#query-keyword-suggestions)
- [`query_phrase_suggestions`](#query-phrase-suggestions)
- [`query_target_cpa_suggestion`](#query-target-cpa-suggestion)

## `apply_daily_budget_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations daily-budget-apply`
- Usage: `Usage: asa recommendations daily-budget-apply [OPTIONS]`
- SDK contract: `POST /recommendations/daily-budgets/apply`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, apply_daily_cap_recommendation`
- Body parameters: `[{"annotation":"List[ApplyDailyCapRecommendation]","container":"list","default":null,"model":"apple_ads_platform.models.apply_daily_cap_recommendation.ApplyDailyCapRecommendation","name":"apply_daily_cap_recommendation","required":true,"wire_name":"body"}]`
- Returns: `RecommendationApplyDailyBudgetResponse`
- CLI help: Daily budget apply recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
- Special handling: `["recommendation-apply"]`

### Request model `apple_ads_platform.models.apply_daily_cap_recommendation.ApplyDailyCapRecommendation`

Request to apply or dismiss a daily budget recommendation

- Schema SHA-256: `ea970a1ac8b33e6ada9b314d0785a843b2db640cf91451401dfcf5da98e75537`
- Source SHA-256: `887ad2985aa3ed3ed4f2c0cdf55205e877343d02971b040f0add06e9db5311d7`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `appliedDailyBudget` | no | `RecommendationMoney | null` | `None` |  |
| `historyId` | no | `string | null` | `None` | Optional history ID for tracking |
| `id` | yes | `string` | — | Recommendation ID to apply/dismiss |
| `promotedObjectId` | yes | `string` | — | Campaign identifier |
| `promotedObjectType` | yes | `string` | — | Type of promoted object |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
[
  {
    "id": "<string>",
    "promotedObjectId": "<string>",
    "promotedObjectType": "<string>"
  }
]
```

#### Referenced structures

##### `RecommendationMoney`

Monetary amount with currency

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | Decimal amount as string (e.g., "1.50") |
| `currency` | yes | `string` | — | ISO 4217 currency code |

## `dismiss_daily_budget_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations daily-budget-dismiss`
- Usage: `Usage: asa recommendations daily-budget-dismiss [OPTIONS]`
- SDK contract: `POST /recommendations/daily-budgets/dismiss`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, apply_daily_cap_recommendation`
- Body parameters: `[{"annotation":"List[ApplyDailyCapRecommendation]","container":"list","default":null,"model":"apple_ads_platform.models.apply_daily_cap_recommendation.ApplyDailyCapRecommendation","name":"apply_daily_cap_recommendation","required":true,"wire_name":"body"}]`
- Returns: `RecommendationDismissDailyBudgetResponse`
- CLI help: Daily budget dismiss recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
- Special handling: `["recommendation-dismiss"]`

### Request model `apple_ads_platform.models.apply_daily_cap_recommendation.ApplyDailyCapRecommendation`

Request to apply or dismiss a daily budget recommendation

- Schema SHA-256: `ea970a1ac8b33e6ada9b314d0785a843b2db640cf91451401dfcf5da98e75537`
- Source SHA-256: `887ad2985aa3ed3ed4f2c0cdf55205e877343d02971b040f0add06e9db5311d7`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `appliedDailyBudget` | no | `RecommendationMoney | null` | `None` |  |
| `historyId` | no | `string | null` | `None` | Optional history ID for tracking |
| `id` | yes | `string` | — | Recommendation ID to apply/dismiss |
| `promotedObjectId` | yes | `string` | — | Campaign identifier |
| `promotedObjectType` | yes | `string` | — | Type of promoted object |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
[
  {
    "id": "<string>",
    "promotedObjectId": "<string>",
    "promotedObjectType": "<string>"
  }
]
```

#### Referenced structures

##### `RecommendationMoney`

Monetary amount with currency

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | Decimal amount as string (e.g., "1.50") |
| `currency` | yes | `string` | — | ISO 4217 currency code |

## `query_daily_budget_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations daily-budget-query`
- Usage: `Usage: asa recommendations daily-budget-query [OPTIONS]`
- SDK contract: `POST /recommendations/daily-budgets/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryDailyBudgetResponse`
- CLI help: Daily budget query recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `apply_target_cpa_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations target-cpa-apply`
- Usage: `Usage: asa recommendations target-cpa-apply [OPTIONS]`
- SDK contract: `POST /recommendations/target-cpas/apply`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, apply_target_cpa_recommendation`
- Body parameters: `[{"annotation":"List[ApplyTargetCpaRecommendation]","container":"list","default":null,"model":"apple_ads_platform.models.apply_target_cpa_recommendation.ApplyTargetCpaRecommendation","name":"apply_target_cpa_recommendation","required":true,"wire_name":"body"}]`
- Returns: `RecommendationApplyTargetCpaResponse`
- CLI help: Target cpa apply recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
- Special handling: `["recommendation-apply"]`

### Request model `apple_ads_platform.models.apply_target_cpa_recommendation.ApplyTargetCpaRecommendation`

Request to apply or dismiss a target CPA recommendation

- Schema SHA-256: `df3c8ad3de3b431ce45c9c0f310d1bdc37a67c280e5dcd4b27fb7cff8b97dac3`
- Source SHA-256: `b7f28fd11118d4c9e30a9b8c09b6875f92652aae1e3dd5bdb797407d94e4a86f`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `appliedTargetCPA` | no | `RecommendationMoney | null` | `None` |  |
| `historyId` | no | `string | null` | `None` | Optional history ID for tracking |
| `id` | yes | `string` | — | Recommendation ID to apply/dismiss |
| `promotedObjectId` | yes | `string` | — | Campaign identifier |
| `promotedObjectType` | yes | `string` | — | Type of promoted object |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
[
  {
    "id": "<string>",
    "promotedObjectId": "<string>",
    "promotedObjectType": "<string>"
  }
]
```

#### Referenced structures

##### `RecommendationMoney`

Monetary amount with currency

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | Decimal amount as string (e.g., "1.50") |
| `currency` | yes | `string` | — | ISO 4217 currency code |

## `dismiss_target_cpa_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations target-cpa-dismiss`
- Usage: `Usage: asa recommendations target-cpa-dismiss [OPTIONS]`
- SDK contract: `POST /recommendations/target-cpas/dismiss`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `x_ap_context, apply_target_cpa_recommendation`
- Body parameters: `[{"annotation":"List[ApplyTargetCpaRecommendation]","container":"list","default":null,"model":"apple_ads_platform.models.apply_target_cpa_recommendation.ApplyTargetCpaRecommendation","name":"apply_target_cpa_recommendation","required":true,"wire_name":"body"}]`
- Returns: `RecommendationDismissTargetCpaResponse`
- CLI help: Target cpa dismiss recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |
- Special handling: `["recommendation-dismiss"]`

### Request model `apple_ads_platform.models.apply_target_cpa_recommendation.ApplyTargetCpaRecommendation`

Request to apply or dismiss a target CPA recommendation

- Schema SHA-256: `df3c8ad3de3b431ce45c9c0f310d1bdc37a67c280e5dcd4b27fb7cff8b97dac3`
- Source SHA-256: `b7f28fd11118d4c9e30a9b8c09b6875f92652aae1e3dd5bdb797407d94e4a86f`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `appliedTargetCPA` | no | `RecommendationMoney | null` | `None` |  |
| `historyId` | no | `string | null` | `None` | Optional history ID for tracking |
| `id` | yes | `string` | — | Recommendation ID to apply/dismiss |
| `promotedObjectId` | yes | `string` | — | Campaign identifier |
| `promotedObjectType` | yes | `string` | — | Type of promoted object |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
[
  {
    "id": "<string>",
    "promotedObjectId": "<string>",
    "promotedObjectType": "<string>"
  }
]
```

#### Referenced structures

##### `RecommendationMoney`

Monetary amount with currency

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `amount` | yes | `string` | — | Decimal amount as string (e.g., "1.50") |
| `currency` | yes | `string` | — | ISO 4217 currency code |

## `query_target_cpa_recommendations`

- Status: `implemented`
- Canonical command: `asa recommendations target-cpa-query`
- Usage: `Usage: asa recommendations target-cpa-query [OPTIONS]`
- SDK contract: `POST /recommendations/target-cpas/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryTargetCpaResponse`
- CLI help: Target cpa query recommendations.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `query_category_suggestions`

- Status: `implemented`
- Canonical command: `asa suggestions categories`
- Usage: `Usage: asa suggestions categories [OPTIONS]`
- SDK contract: `POST /suggestions/categories/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryCategorySuggestionResponse`
- CLI help: Categories suggestions.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `query_keyword_suggestions`

- Status: `implemented`
- Canonical command: `asa suggestions keywords`
- Usage: `Usage: asa suggestions keywords [OPTIONS]`
- SDK contract: `POST /suggestions/keywords/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryKeywordSuggestionResponse`
- CLI help: Keywords suggestions.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `query_phrase_suggestions`

- Status: `implemented`
- Canonical command: `asa suggestions phrases`
- Usage: `Usage: asa suggestions phrases [OPTIONS]`
- SDK contract: `POST /suggestions/phrases/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryPhraseSuggestionResponse`
- CLI help: Phrases suggestions.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

## `query_target_cpa_suggestion`

- Status: `implemented`
- Canonical command: `asa suggestions target-cpa`
- Usage: `Usage: asa suggestions target-cpa [OPTIONS]`
- SDK contract: `POST /suggestions/target-cpas/query`
- Context: `required`
- Mutation: `no`
- Pagination: `recommendation-pagination`
- Required SDK parameters: `x_ap_context, recommendation_query_request`
- Body parameters: `[{"annotation":"RecommendationQueryRequest","container":"model","default":null,"model":"apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest","name":"recommendation_query_request","required":true,"wire_name":"body"}]`
- Returns: `RecommendationQueryTargetCpaSuggestionResponse`
- CLI help: Target cpa suggestions.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | yes | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.recommendation_query_request.RecommendationQueryRequest`

Structured query request for filtering, sorting, and paginating recommendations. **Required Filters:** - `promotedObjectId` - Campaign or app identifier (REQUIRED) - `promotedObjectType` - Type of promoted object (REQUIRED) **Pagination:** - Default offset: 0 - Default pageSize: 20 **Field Selection:** - Specify `fields` array to reduce payload size - Omit `fields` to receive all available fields

- Schema SHA-256: `43f95235a37b2f1f6ea1a8e50c51381fb45b2ddbccf606703e88c6c4608cfbf2`
- Source SHA-256: `92ea27c037c5fc96db6f87de0dfd9958b358c04a97a00bb3a860f488ef9fcc21`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `filters` | no | `array[RecommendationFilterCondition] | null` | `None` | Filter conditions (promotedObjectId and promotedObjectType are REQUIRED) |
| `pagination` | no | `RecommendationQueryRequestPagination | null` | `None` |  |
| `sorting` | no | `array[RecommendationSorting] | null` | `None` | Sort order for results (multiple fields supported) |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "filters": [
    {
      "field": "<string>",
      "operator": "<one of: EQUALS | NOT_EQUALS | IN | CONTAINS_ANY | CONTAINS_ALL | LESS_THAN | LESS_THAN_OR_EQUAL_TO | GREATER_THAN | GREATER_THAN_OR_EQUAL_TO | BETWEEN | STARTS_WITH | ENDS_WITH | LIKE | unknown_default_open_api>",
      "value": [
        "<string>"
      ]
    }
  ],
  "pagination": {
    "offset": 0,
    "pageSize": 0
  },
  "sorting": [
    {
      "field": "<string>"
    }
  ]
}
```

#### Referenced structures

##### `RecommendationFilterCondition`

Individual filter condition for querying recommendations. **Operator Support by Field Type:** - String fields: EQUALS, IN, STARTS_WITH, CONTAINS, LIKE - Numeric fields: EQUALS, IN, GREATER_THAN, LESS_THAN, BETWEEN - Date fields: EQUALS, GREATER_THAN, LESS_THAN - Enum fields: EQUALS, IN - List fields: CONTAINS_ANY, CONTAINS_ALL

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to filter on (must match model field names) |
| `ignoreCase` | no | `boolean | null` | `False` | Case-insensitive matching for string fields |
| `operator` | yes | `RecommendationFilterOperator` | — |  |
| `value` | yes | `array[string]` | — | Filter values (always array, even for single values) |

##### `RecommendationFilterOperator`

Filter operator for query conditions

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `RecommendationQueryRequestPagination`

Pagination parameters

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `offset` | no | `integer | null` | `0` | Number of items to skip |
| `pageSize` | no | `integer | null` | `20` | Number of items per page |

##### `RecommendationSorting`

Sort specification for query results

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `field` | yes | `string` | — | Field name to sort by |
| `order` | no | `RecommendationSortingOrder | null` | `ASC` |  |

##### `RecommendationSortingOrder`

Sort direction

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
