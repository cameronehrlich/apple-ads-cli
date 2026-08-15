# ASA CLI — API Completion Plan

Complete coverage of the legacy Apple Ads Campaign Management API v5.

## Current State

### Implemented (api.py → commands/)
| Area | API Methods | CLI Commands |
|------|-------------|--------------|
| **Campaigns** | get_campaigns, get_campaign, create_campaign, update_campaign, pause_campaign, enable_campaign, delete_campaign | campaigns list, create, audit, pause, enable |
| **Ad Groups** | get_ad_groups, create_ad_group, update_ad_group, delete_ad_group | adgroups list, create |
| **Targeting Keywords** | get_keywords, add_keywords, delete_keywords, update_keyword_bid, pause_keyword, enable_keyword | keywords list, add, delete, update-bid, pause, enable, promote |
| **Campaign Negatives** | get_negative_keywords, add_negative_keywords | keywords add-negatives (partial) |
| **Ad Group Negatives** | add_ad_group_negative_keywords | (used internally by keyword routing) |
| **Reports** | get_campaign_report, get_keyword_report, get_ad_group_report, get_search_terms_report, get_impression_share_report | reports summary, keywords, adgroups, search-terms, impression-share |
| **Optimization** | (logic layer) | optimize (auto-promote from Discovery) |

### Missing from API v5

Listed by priority for our use case.

---

## Phase 1 — High Value (affects daily workflow)

### 1.1 Negative Keyword Management (Complete CRUD)
**Why:** We can add negatives but can't list or delete them. If we add a bad negative by mistake, we have to use the web UI.

**API endpoints:**
- `GET /campaigns/{id}/negativekeywords` — already have `get_negative_keywords`
- `DELETE /campaigns/{id}/negativekeywords/delete/bulk` — **MISSING**
- `GET /campaigns/{id}/adgroups/{id}/negativekeywords` — **MISSING** (list at ad group level)
- `DELETE /campaigns/{id}/adgroups/{id}/negativekeywords/delete/bulk` — **MISSING**
- `PUT /campaigns/{id}/negativekeywords/bulk` — **MISSING** (update status)

**CLI commands to add:**
- `keywords list-negatives [--campaign ID]` — show all negatives for a campaign
- `keywords delete-negative [--campaign ID] [--keyword ID]` — remove a negative
- `keywords list-negatives --ad-group ID` — show ad-group-level negatives

**Tests:**
- `test_get_ad_group_negative_keywords` — mock paginated response
- `test_delete_negative_keywords_success` — mock bulk delete
- `test_delete_negative_keywords_not_found` — error handling
- `test_list_negatives_command` — CLI integration test

### 1.2 Bulk Keyword Updates
**Why:** We currently update bids one keyword at a time in a loop. The API supports bulk updates — one call for all keywords. This would have saved ~60 API calls when we bumped all bids earlier.

**API endpoint:**
- `PUT /campaigns/{id}/adgroups/{id}/targetingkeywords/bulk` — **partial** (we use it for single updates, not true bulk)

**Changes:**
- `api.py`: Add `update_keywords_bulk(campaign_id, ad_group_id, updates: list[dict])` that batches keyword updates
- `commands/keywords.py`: Add `keywords update-bids --campaign ID --bid AMOUNT` to update all keywords in a campaign at once
- Refactor the existing for-loop bid updates to use bulk endpoint

**Tests:**
- `test_bulk_keyword_update_success` — multiple keyword IDs, verify single API call
- `test_bulk_keyword_update_partial_failure` — some succeed, some fail
- `test_update_bids_command_all` — CLI test for campaign-wide bid change

### 1.3 Custom Reports (Async)
**Why:** Current reports are synchronous and limited. Custom reports support larger date ranges, more granular dimensions, and async generation for big datasets.

**API endpoints:**
- `POST /custom-reports` — create async report
- `GET /custom-reports/{id}` — check report status / download

**CLI commands:**
- `reports custom --days 90 --granularity WEEKLY` — create and poll for async report
- `reports custom-status --id ID` — check status of pending report

**Tests:**
- `test_create_custom_report` — verify request payload
- `test_poll_custom_report_pending` — status polling
- `test_poll_custom_report_complete` — download results

---

## Phase 2 — Medium Value (fills gaps)

### 2.1 Geo Targeting
**Why:** Allows targeting/excluding specific regions. Not critical for US-only campaigns but needed for international expansion.

**API endpoints:**
- `POST /search/geo` — search for geo locations
- `GET /geodata/{countryOrRegion}/admin-areas` — get states/provinces
- `GET /geodata/{countryOrRegion}/admin-areas/{id}/localities` — get cities

**CLI commands:**
- `campaigns geo-search --query "California"` — find geo entities
- `campaigns set-geo --campaign ID --include "US-CA,US-NY"` — set geo targeting

**Tests:**
- `test_geo_search` — mock search response
- `test_get_admin_areas` — country subdivision lookup

### 2.2 Campaign Negative Keywords at Ad Group Level (list/delete)
Already covered in 1.1 above.

### 2.3 Ad Creative / Ad Variations
**Why:** API v5 replaced creative sets with ad variations. Allows managing which app screenshots/previews show for different keyword themes.

**API endpoints:**
- `GET /campaigns/{id}/adgroups/{id}/ads` — list ads
- `POST /campaigns/{id}/adgroups/{id}/ads` — create ad
- `PUT /campaigns/{id}/adgroups/{id}/ads/{id}` — update ad
- `DELETE /campaigns/{id}/adgroups/{id}/ads/{id}` — delete ad

**CLI commands:**
- `ads list --campaign ID` — list ad variations
- `ads create --campaign ID --ad-group ID` — create ad variation

**Tests:**
- `test_get_ads` — list ad variations
- `test_create_ad` — verify payload structure

---

## Phase 3 — Low Priority (completeness)

### 3.1 Budget Orders
**Why:** Manage billing. Most users handle this in the web UI. Only relevant for programmatic budget management.

**API endpoints:**
- `GET /budgetorders` — list budget orders
- `GET /budgetorders/{id}` — get specific order
- `POST /budgetorders` — create order
- `PUT /budgetorders/{id}` — update order

### 3.2 ACL / User Management
**Why:** Manage API user roles and org access. One-time setup, not daily workflow.

**API endpoints:**
- `GET /acls` — list access control entries
- `PUT /useracls/{userId}` — update user access

### 3.3 Keyword Recommendations (if available in v5)
**Why:** We attempted this and got 404s. The sosumi research agent is currently investigating whether these endpoints exist in v5 or were removed. If they exist, add them; if not, document the gap.

**Pending investigation results.**

---

## Testing Strategy

### Test Structure
```
tests/
├── test_api.py              # Existing — API client unit tests
├── test_config.py           # Existing — config tests
├── test_negative_keywords.py  # NEW — Phase 1.1
├── test_bulk_operations.py    # NEW — Phase 1.2
├── test_custom_reports.py     # NEW — Phase 1.3
├── test_geo.py                # NEW — Phase 2.1
├── test_ads.py                # NEW — Phase 2.3
└── test_integration.py        # NEW — end-to-end with real API (gated)
```

### Unit Test Pattern (all phases)
Every API method gets:
1. **Happy path** — mock successful response, verify return value
2. **Error handling** — mock API error (404, 400, rate limit), verify graceful failure
3. **Pagination** — if applicable, mock multi-page response
4. **Edge cases** — empty inputs, duplicate handling

### Integration Tests (optional, gated behind `--integration` flag)
- Real API calls against our actual ASA account
- Marked with `@pytest.mark.integration`
- Skipped by default: `pytest -m "not integration"`
- Validates that endpoint paths, request shapes, and auth actually work
- **Read-only only** — never create/delete/modify real campaigns in integration tests

### Running Tests
```bash
# Unit tests only (fast, no API calls)
cd ~/apple-ads-cli && uv run pytest tests/ -v

# Including integration tests (requires API credentials)
cd ~/apple-ads-cli && uv run pytest tests/ -v -m integration
```

---

## Implementation Order

1. **Phase 1.1** — Negative keyword CRUD (2-3 hours)
   - Add API methods → Add CLI commands → Write tests
2. **Phase 1.2** — Bulk keyword updates (1-2 hours)
   - Refactor update_keyword_bid → Add bulk method → Update CLI → Tests
3. **Phase 1.3** — Custom reports (2-3 hours)
   - Add async report API → Add CLI with polling → Tests
4. **Phase 2.1** — Geo targeting (2 hours)
5. **Phase 2.3** — Ad variations (2 hours)
6. **Phase 3** — Budget orders, ACL (1 hour each, low priority)

**Total estimated: ~12-15 hours for full API coverage.**

---

## Notes

- The sosumi research agent is currently pulling the complete API v5 endpoint reference from Apple's docs. Once that completes, this plan should be updated with any endpoints we missed.
- All changes should be committed to `~/apple-ads-cli` main branch per Cameron's request.
- The `research` command added during this session is a stub — update it once we confirm whether keyword recommendation endpoints exist in v5.
