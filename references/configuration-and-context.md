# Configuration and request context

Read this reference when authenticating, selecting an account, choosing an advertising surface, or preparing a request model.

## Runtime and SDK

Platform API v1 uses Apple's official `apple-ads-platform` Python package and therefore requires Python 3.12 or newer. Run the repository-pinned environment rather than a globally installed SDK. The generated command catalog records the exact SDK version and source provenance used to inventory endpoints.

Legacy v5 is isolated under `asa v5`. Do not assume v5 organization context, endpoint paths, request models, or response shapes apply to v1.

## Credentials

Authentication uses the Apple Ads client ID, team ID, key ID, and EC private key. Treat the private key, generated client secret, access token, authorization headers, and signed material as secrets.

The legacy organization ID is optional for Platform API v1 configuration and is required only for scoped `asa v5 ...` requests. Save a Platform ad-account ID separately or supply it through `--ad-account` or `ASA_AD_ACCOUNT_ID`; the CLI never substitutes the legacy organization ID.

Never:

- Print secret values or request headers containing them.
- Put private-key contents into a command argument, manifest, fixture, generated reference, or report.
- Commit local credential files.
- Enable SDK body logging for authentication calls.

## Account scope

Platform API campaign scope uses an ad account. The SDK represents the `X-AP-Context` header as `x_ap_context`; the common value is `adAccountId=<id>;`. Use the exact context contract recorded for the operation. Do not substitute the legacy v5 `orgId` value.

Operations can be scoped to:

- An organization or identity context.
- An App Store advertising account and promoted app.
- An Apple Maps business-brand account.
- An ad account shared by an operation's resource hierarchy.

Resolve account and advertiser-resource identity with read-only commands before any mutation. App Store and Maps resources are not interchangeable.

## Request bodies

Use the generated entry's request model and required parameters. For complex bodies, prefer the wrapper's documented JSON file or standard-input mode rather than a large shell argument. Validate locally before sending.

Do not infer a model field from a similarly named v5 property. Generated references list the pinned Pydantic model schema hash so a changed SDK model is detected as catalog drift.

## Implementation status

The SDK inventory proves that an endpoint exists in the pinned client library. It does not prove that the CLI wrapper is registered or accepted by a live Apple account.

- `inventory-only`: present in the SDK manifest, without a registered wrapper.
- `planned`: wrapper design exists but is not runnable.
- `implemented`: runtime command is registered and has contract tests.
- `unverified`: implemented locally but not accepted by a live account.
- `blocked`: live validation is prevented by account capability, delegation, or an upstream Apple failure.
- `live-read-verified` or `live-mutation-verified`: evidence exists for that level only.

Do not promote one status into another without its corresponding evidence.
