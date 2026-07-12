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

This policy currently covers the campaign, ad-group, keyword, campaign-report,
keyword-report, search-term-report, and keyword-within-ad-group reads used by the
optimizer and recurring reporting workflow. Other legacy convenience methods may
still return `None` or an empty list after printing an error; callers should not
use those paths as autonomous mutation evidence until they are migrated.
