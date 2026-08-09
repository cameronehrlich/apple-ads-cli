# API failure handling

The CLI distinguishes a valid empty Apple Ads result from a failed request.
Authentication, transport, HTTP, and invalid-response failures raise
`SearchAdsAPIError` instead of being converted to empty campaign or report data.
Commands therefore exit nonzero rather than reporting a healthy no-op.

OAuth and API requests use bounded connect/read timeouts. Authentication failures
still receive the existing token-refresh retry; other retries are intentionally
not automatic because mutation requests may not be safe to repeat.

For unattended use, run `asa config test` as a preflight and treat any nonzero
exit as a hard stop. A successful preflight with zero campaigns is valid and is
reported as zero campaigns.

This policy covers campaign, ad-group, keyword, campaign-report, keyword-report,
ad-group-report, search-term-report, ad-report, custom-report, and keyword-within-
ad-group reads used by recurring reporting. Stable `--json` commands therefore do
not convert a failed request into a healthy empty report.

Ad creation and CPP experiment attachment require immediate readback of the ad's
name, creative ID, and status. A mutation response without matching readback exits
nonzero and must be treated as unverified. The CLI does not attempt an automatic
rollback because a second mutation may be unsafe to retry.
