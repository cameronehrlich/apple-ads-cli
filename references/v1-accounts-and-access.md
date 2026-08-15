<!-- Generated from the canonical SDK manifest and registered Typer trees. Do not edit by hand. -->

# Accounts and access

SDK `apple-ads-platform` version `1.109.0`; source commit `742ba544433ba9a5bef0ab3603336dcf53ff9338`.

`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.

## Contents

- [`get_user_acls`](#get-user-acls)
- [`get_advertiser_resources`](#get-advertiser-resources)
- [`get_me`](#get-me)
- [`orgs_id_get`](#orgs-id-get)
- [`ad_accounts_post`](#ad-accounts-post)
- [`ad_accounts_id_get`](#ad-accounts-id-get)
- [`ad_accounts_id_put`](#ad-accounts-id-put)

## `get_user_acls`

- Status: `implemented`
- Canonical command: `asa access acls`
- Usage: `Usage: asa access acls [OPTIONS]`
- SDK contract: `GET /acls`
- Context: `none`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `none`
- Body parameters: `[]`
- Returns: `UserAclListResponse`
- CLI help: Acls access.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `get_advertiser_resources`

- Status: `implemented`
- Canonical command: `asa access advertiser-resources`
- Usage: `Usage: asa access advertiser-resources [OPTIONS]`
- SDK contract: `GET /advertiser-resources`
- Context: `none`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `resource_type`
- Body parameters: `[]`
- Returns: `AdvertiserResourceListResponse`
- CLI help: Advertiser resources access.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--resource-type` | yes | `text` | — | — | resourceType parameter |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `get_me`

- Status: `implemented`
- Canonical command: `asa access me`
- Usage: `Usage: asa access me [OPTIONS]`
- SDK contract: `GET /me`
- Context: `none`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `none`
- Body parameters: `[]`
- Returns: `MeResponse`
- CLI help: Me access.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `orgs_id_get`

- Status: `implemented`
- Canonical command: `asa access org`
- Usage: `Usage: asa access org [OPTIONS]`
- SDK contract: `GET /orgs/{id}`
- Context: `none`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id`
- Body parameters: `[]`
- Returns: `OrgResponse`
- CLI help: Org access.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `ad_accounts_post`

- Status: `implemented`
- Canonical command: `asa ad-accounts create`
- Usage: `Usage: asa ad-accounts create [OPTIONS]`
- SDK contract: `POST /ad-accounts`
- Context: `none`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `none`
- Body parameters: `[{"annotation":"Optional[AdAccountCreate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_account_create.AdAccountCreate","name":"ad_account_create","required":false,"wire_name":"body"}]`
- Returns: `AdAccountResponse`
- CLI help: Create ad accounts.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_account_create.AdAccountCreate`

AdAccountCreate

- Schema SHA-256: `7866bb6f09bcea22e2ed98df8d209efa560ec24c6de2fff0ccbec4ab7a36e8c4`
- Source SHA-256: `23ef5d6519e14ee7f34fc9d09c974a9e17741965d181e9887cfe1a92ca4bdcd6`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `delegations` | no | `array[DelegationCreate] | null` | `None` |  |
| `name` | yes | `string` | — |  |
| `productFeatures` | yes | `array[string]` | — |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "name": "<string>",
  "productFeatures": [
    "<string>"
  ]
}
```

#### Referenced structures

##### `AdvertiserResourceType`

AdvertiserResourceType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `DelegationCreate`

DelegationCreate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `resourceId` | yes | `string` | — |  |
| `resourceType` | yes | `AdvertiserResourceType` | — |  |

## `ad_accounts_id_get`

- Status: `implemented`
- Canonical command: `asa ad-accounts get`
- Usage: `Usage: asa ad-accounts get [OPTIONS]`
- SDK contract: `GET /ad-accounts/{id}`
- Context: `required`
- Mutation: `no`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[]`
- Returns: `AdAccountResponse`
- CLI help: Get ad accounts.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

## `ad_accounts_id_put`

- Status: `implemented`
- Canonical command: `asa ad-accounts update`
- Usage: `Usage: asa ad-accounts update [OPTIONS]`
- SDK contract: `PUT /ad-accounts/{id}`
- Context: `required`
- Mutation: `yes`
- Pagination: `none`
- Required SDK parameters: `id, x_ap_context`
- Body parameters: `[{"annotation":"Optional[AdAccountUpdate]","container":"model","default":"None","model":"apple_ads_platform.models.ad_account_update.AdAccountUpdate","name":"ad_account_update","required":false,"wire_name":"body"}]`
- Returns: `AdAccountResponse`
- CLI help: Update ad accounts.

### Exact CLI inputs

| Kind | Name or flags | Required | Type | Default | Environment | Help |
|---|---|---|---|---|---|---|
| option | `--id` | yes | `text` | — | — | id parameter |
| option | `--file` | no | `path` | — | — | JSON request file; use '-' to read from stdin |
| option | `--ad-account` | no | `text` | — | `ASA_AD_ACCOUNT_ID` | Apple Ads Platform ad account ID |
| option | `--dry-run` | no | `boolean` | `False` | — | Validate and print the SDK call without sending it |
| option | `--confirm` | no | `boolean` | `False` | — | Confirm this Apple Ads mutation |
| option | `--help` | no | `boolean` | `False` | — | Show this message and exit. |

### Request model `apple_ads_platform.models.ad_account_update.AdAccountUpdate`

AdAccountUpdate

- Schema SHA-256: `7e9e30df441e6bc4ba4217e15fd5aafc2f5e632889337c33845fff410be6e315`
- Source SHA-256: `789484a45730046e085e44a8650dcec0ad06f19917573237c8bfc88eb38da3a1`

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `delegations` | no | `array[DelegationUpdate] | null` | `None` |  |
| `name` | no | `string | null` | `None` |  |
| `productFeatures` | no | `array[string] | null` | `None` |  |

Required-field body skeleton (replace every placeholder and add optional fields only as needed):

```json
{
  "delegations": [
    {
      "resourceId": "<string>",
      "resourceType": "<one of: CONTENT_PROVIDER | BUSINESS_BRAND | unknown_default_open_api>"
    }
  ],
  "name": "<string>",
  "productFeatures": [
    "<string>"
  ]
}
```

#### Referenced structures

##### `AdvertiserResourceType`

AdvertiserResourceType

| Field | Required | Type | Default | Description |
|---|---|---|---|---|

##### `DelegationUpdate`

DelegationUpdate

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `resourceId` | no | `string | null` | `None` |  |
| `resourceType` | no | `AdvertiserResourceType | null` | `None` |  |
