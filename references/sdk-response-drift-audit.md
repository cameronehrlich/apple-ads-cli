# SDK response-drift audit

This audit covers `apple-ads-platform==1.109.0`. It distinguishes a generated
SDK contract from live Apple acceptance: a matching local model does not prove
that an endpoint is enabled, and one successful account response does not prove
that every possible response shape is compatible.

## Deterministic inventory

The generated manifest reconciles all 99 canonical operations to 71 root
response types and the complete 220-model response closure. Those models expose
1,391 fields, including:

- 516 strict fields
- 135 identifier-like fields
- 101 enum-backed fields
- 15 fields with custom Pydantic validators

Every response model records its JSON Schema hash, generated source hash, and
the names of strict, identifier, enum, and custom-validator fields. An SDK
upgrade therefore fails the manifest drift gate even if its operation count
does not change.

## Confirmed live mismatches

Two wire/model disagreements are confirmed with sanitized live responses:

1. App keyword and search-term report metadata returns keyword status
   `ENABLED`; the generated `ReportingKeyword` validator accepts `ACTIVE`,
   `PAUSED`, or `DELETED`.
2. Impression-share rows return numeric `promotedObjectId`; the generated
   `ImpressionShareRow` requires a strict string.

The compatibility hook preserves the original JSON only for those exact root
response types and conditions. It validates a copied payload after replacing
only the known mismatch for validation purposes. That second SDK pass prevents
an accepted first-row mismatch from hiding an unrelated error in a later row.
Boolean and floating-point IDs are rejected; Python's `bool`/`int` inheritance
does not relax the wire contract.

## Sibling risk review

`BrandsReportingKeyword.status` has the same generated `ACTIVE` validator as
`ReportingKeyword.status`, so business-brand keyword reports are the closest
sibling risk. The available account is not eligible for business-brand reports,
so no live mismatch is confirmed. `BrandsKeywordReportResponse` intentionally
remains outside the compatibility allowlist and a regression test requires it
to fail closed on `ENABLED`.

Eleven reachable models declare `promotedObjectId` as a strict string. Safe
reads confirmed strings in campaign resources and app campaign reports, while
impression share alone returned a number. Recommendation, asset, rejection,
history, and business-brand variants were empty, unavailable, or ineligible in
the audited account. They remain strict and receive no speculative coercion.

The other custom-validator surfaces include app device classes, eligibility,
creative rejection levels, error codes, geo-block reasons, locations, location
groups, product-page device classes, and geo rules. Available app, locale,
campaign, ad-group, keyword, negative-keyword, product-page, shared-budget,
report, insight, recommendation, and suggestion safe reads produced no further
deserialization mismatch. Empty and ineligible responses are not proof of full
shape compatibility.

## Adding a compatibility case

1. Capture a sanitized live response and the original SDK `ValidationError`.
2. Identify the exact root response type, nested wire field, rejected value or
   type, and Pydantic error type.
3. Add a positive fixture plus sibling, adjacent-field, adjacent-type, malformed
   JSON, and later-row failure tests.
4. Patch only a copied payload for full SDK validation; return the unchanged
   original JSON after validation succeeds.
5. Keep every unrecognized response and mixed-error payload fail closed.
6. Run manifest, generated-skill, full test, packaging, and safe-read gates.

Never use a mutation to probe response compatibility.
