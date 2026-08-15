# Safety and output contracts

Read this reference before mutations, unattended use, report comparisons, or integrations that consume JSON.

## Failure is not empty data

Authentication, transport, HTTP, deserialization, and invalid-response failures must exit nonzero. Never convert them into an empty campaign list, report, recommendation set, or healthy no-op.

The official SDK deserializer is authoritative by default. A compatibility
fallback is allowed only for a sanitized, live-confirmed response mismatch with
an exact response type, field path, rejected type/value, and regression fixture.
Validate a patched copy of the complete response through the SDK before
returning the original raw JSON; otherwise a known first-row error can hide a
different failure later in the payload. Boolean values must never be accepted
as integer identifiers merely because Python treats `bool` as a subclass of
`int`.

Use bounded connection and read timeouts. Token refresh may retry authentication. Do not automatically retry other mutation requests because the first request may have succeeded even when the response was lost.

For unattended work, run the documented read-only preflight first and treat any nonzero exit as a hard stop.

## Mutation sequence

1. Resolve the exact ad account and resource IDs with reads.
2. Validate the request model locally.
3. Present the exact targets and before/after values unless already authorized.
4. Use the command's documented mutation gate.
5. Capture the returned resource or operation ID.
6. Read the resource back and compare every intended field.
7. Report the mutation and readback as separate receipts.

A successful HTTP response without matching readback is unverified. Do not attempt an automatic rollback after an ambiguous failure.

Delete, recommendation apply/dismiss, asset upload/delete, account/delegation changes, and bulk partial-success operations need particular care. For partial success, report each item by correlation ID and do not describe the batch as wholly successful.

## Reporting windows

Use inclusive completed calendar dates. Default windows should end yesterday; reject today or a future date when a complete-window comparison is required. State the time zone and distinguish a complete inventory from performance-only rows.

Stable machine output should include:

- A schema version and report type.
- Inclusive start and end dates, day count, time zone, and completeness.
- Numeric money and rates, with missing ratios represented as `null`.
- Deterministically ordered rows.
- An `inventory_complete` indicator when absence-based analysis is allowed.

Do not interpret a performance-only report as proof that a keyword, ad, campaign, recommendation, or search term does not exist.

## v1 insights

Impression share is a bounded paid-visibility measurement, not organic rank, share of installs, exact search volume, or competitor bid data. Distinguish first-slot share from all-slot share.

Search-term popularity is market-level relative demand, not the app's own traffic or exact query volume. Record country or region, genre, and weekly or monthly period with the results.

## Legacy v5 reports

The v5 impression-share flow creates an asynchronous custom report and downloads a short-lived CSV. Reuse a known report ID where supported, observe Apple's date-window and creation limits, and download completed results promptly.

## Experiments and custom product pages

App Store Connect remains the custom-product-page authoring system. A workflow may validate an existing creative and attach it to an ad group, but attachment is a mutation and requires immediate readback of ad ID, name, creative ID, and status. Measurement policy belongs to the caller; the general CLI should return complete-window evidence rather than make unsupported causal claims.
