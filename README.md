# 🍎 Apple Search Ads CLI

> **The missing command-line interface for Apple Search Ads.** Manage campaigns, keywords, and reporting using Apple's recommended 4-campaign structure.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Apple Ads API v5](https://img.shields.io/badge/Apple%20Ads%20API-v5-black.svg)](https://developer.apple.com/documentation/apple_ads)

```bash
# Add keywords with automatic routing
$ asa keywords add "photo editor,image filter" --type category

✓ Added 2 keywords to Category campaign (exact match)
✓ Added 2 keywords to Discovery campaign (broad match)
✓ Added 2 negative keywords to Discovery (prevents overlap)
```

## ✨ Features

- **🎯 4-Campaign Structure** — Implements Apple's best practices with Brand, Category, Competitor, and Discovery campaigns
- **🔀 Smart Keyword Routing** — Add keywords once; they're automatically distributed to the right campaigns with the right match types
- **📈 Automated Optimization** — One command analyzes Discovery, promotes winners, and blocks losers
- **📊 Rich Reporting** — Performance summaries, keyword reports, search term analysis, impression share, ad-level reports, bid recommendations, and async custom reports
- **💰 Budget Management** — Monitor budget orders, check campaign budget health with color-coded status
- **🌍 Geo Targeting** — Search locations, view and set campaign geo targeting by country/region
- **🎨 Ad Management** — List, create, and delete ad variations; manage creatives and product pages; view rejection reasons
- **🔐 Access Control** — List ACLs, check user info, search apps, verify eligibility, list supported countries
- **📦 Bulk Operations** — Bulk keyword bid updates, bulk negative keyword management, cross-campaign keyword search
- **🔒 Dry-Run Mode** — Preview every change before it happens
- **🤖 Claude Code Integration** — Includes SKILL.md for AI-assisted campaign management

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/cameronehrlich/apple-search-ads-cli.git
cd apple-search-ads-cli

# Run with uv (recommended, no install needed)
uv run asa --help

# Or install with pip
pip install -e .
asa --help
```

### Setup

```bash
# Configure your Apple Ads API credentials
asa config setup

# Test connection
asa config test

# Audit your existing campaigns
asa campaigns audit
```

<details>
<summary>📝 Getting API Credentials</summary>

1. Go to [Apple Ads](https://ads.apple.com/) → **Account Settings** → **API**
2. Create an API user with appropriate permissions
3. Generate an EC key pair:
   ```bash
   openssl ecparam -genkey -name prime256v1 -noout -out private-key.pem
   openssl ec -in private-key.pem -pubout -out public-key.pem
   ```
4. Upload the public key to Apple Ads dashboard
5. Note your **Client ID**, **Team ID**, **Key ID**, and **Org ID**

</details>

## 📖 Usage

### Campaign Management

```bash
# List all campaigns
asa campaigns list

# Audit against Apple's recommendations
asa campaigns audit --verbose

# Create the 4-campaign structure
asa campaigns setup --countries US --budget 50 --dry-run
asa campaigns setup --countries US --budget 50

# Pause/enable campaigns
asa campaigns pause --all
asa campaigns enable 12345678
```

### Keywords

```bash
# Add keywords (automatically routes to correct campaigns)
asa keywords add "my app,myapp" --type brand
asa keywords add "photo editor,image filter" --type category
asa keywords add "vsco,snapseed" --type competitor

# Block irrelevant terms
asa keywords add-negatives "auto clicker,testflight,crypto" --all

# Promote winning keywords from Discovery
asa keywords promote "best photo app" --target category

# List and filter keywords
asa keywords list --campaign 12345
asa keywords list --filter "photo" --status ACTIVE

# Negative keyword management
asa keywords list-negatives                    # List all negatives
asa keywords delete-negatives 123,456          # Remove negatives by ID

# Search across campaigns
asa keywords find "photo"                      # Find keywords matching text

# Bulk bid updates
asa keywords update-bids-bulk --bid 2.50       # Update all bids at once
```

### Reporting

```bash
# Performance summary
asa reports summary --days 7

# Keyword performance (sortable)
asa reports keywords --sort cpa

# Search term analysis
asa reports search-terms --winners    # Terms worth promoting
asa reports search-terms --negatives  # Terms to block

# Impression share / Share of Voice
asa reports impression-share --all

# Ad-level performance
asa reports ads

# Bid recommendations (from Apple's keyword insights)
asa reports bid-recommendations

# Async custom reports (large date ranges)
asa reports custom --days 90 --granularity WEEKLY
asa reports custom-list                        # List pending/completed reports
asa reports custom-get <ID>                    # Download specific report
```

### Budget Management

```bash
# List budget orders
asa budget list

# Campaign budget health (color-coded)
asa budget status

# Get budget order details
asa budget get <ID>

# Create a budget order
asa budget create --name "Q1 2025" --amount 5000 --start 2025-01-01 --end 2025-03-31
```

### Geo Targeting

```bash
# Search for geo locations
asa geo search "California"

# Show campaign geo targeting
asa geo show

# Set geo targeting
asa geo set --campaign <ID> --countries US,CA,GB
```

### Ads & Creatives

```bash
# List ad variations
asa ads list --campaign <ID>

# Create/delete ad variations
asa ads create --campaign <ID> --ad-group <ID>
asa ads delete <AD_ID> --campaign <ID> --ad-group <ID>

# View creative sets and product pages
asa ads creatives --campaign <ID> --ad-group <ID>
asa ads product-pages

# Check ad rejection reasons
asa ads rejections
```

### Access Control

```bash
# List access control entries
asa acl list

# Current user info
asa acl me

# Search for apps eligible for ads
asa acl search-apps "My App"

# Check campaign eligibility
asa acl eligibility <APP_ID>

# List supported countries
asa acl countries
```

### Automated Optimization

The `optimize` command is your weekly campaign maintenance in one line:

```bash
# Preview changes
asa optimize --dry-run

# Run with confirmation
asa optimize

# Fully automated (for cron jobs)
asa optimize --auto-approve
```

**What it does:**
1. Analyzes Discovery search terms (last 14 days)
2. Identifies **winners**: ≥2 installs, CPA ≤ $5
3. Identifies **losers**: ≥$1 spend, 0 installs
4. Promotes winners → exact match in target campaign + negative in Discovery
5. Blocks losers in Discovery by default (`--negative-scope managed` is explicit)

```bash
# Customize thresholds
asa optimize --days 7 --cpa-threshold 3.00 --min-installs 3 --min-spend 2.00
```

## 🏗️ Campaign Structure

Apple recommends a **4-campaign structure** that separates intent and controls costs:

| Campaign | Purpose | Match Type | Search Match |
|----------|---------|------------|--------------|
| **Brand** | Your app/company name | Exact | OFF |
| **Category** | What your app does | Exact | OFF |
| **Competitor** | Other apps users might try | Exact | OFF |
| **Discovery** | Find new keywords | Broad | ON |

### How Keyword Routing Works

When you run `asa keywords add "term" --type category`:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   "term" ──┬──► Category Campaign (EXACT)                       │
│            │    Bids on exact matches only                      │
│            │                                                    │
│            ├──► Discovery Campaign (BROAD)                      │
│            │    Finds related search terms                      │
│            │                                                    │
│            └──► Discovery Campaign (NEGATIVE)                   │
│                 Prevents bidding on exact term in Discovery     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

This ensures:
- ✅ Maximum control over high-value exact terms
- ✅ Continued discovery of related search terms
- ✅ No duplicate spend on the same intent

## 📁 Configuration

Configuration is stored in `~/.asa-cli/`:

```
~/.asa-cli/
├── credentials.json    # API credentials (chmod 600)
└── config.json         # App settings (ID, name, countries, default bid)
```

## 🔧 API Behavior

| Feature | Behavior |
|---------|----------|
| **Error Handling** | Reports both successes and errors; duplicates don't fail the operation |
| **Authentication** | Auto-refreshes expired tokens with up to 2 retries |
| **Pagination** | Automatically handles large result sets (>1000 items) |
| **Rate Limiting** | Respects Apple's API limits |

## 📡 API Coverage

Full Apple Search Ads Campaign Management API v5 coverage — 72 API methods across 15 categories:

| Category | Operations |
|----------|------------|
| **Campaigns** | list, get, create, update, pause, enable, delete |
| **Ad Groups** | list, create, update, pause, enable, delete |
| **Targeting Keywords** | list, add, find, delete, update bid, bulk update bids, pause, enable |
| **Campaign Negatives** | list, find, add, update, delete |
| **Ad Group Negatives** | list, find, add, update, delete |
| **Reports** | campaign, keyword, ad group, search terms, impression share |
| **Custom Reports** | create (async), get, list |
| **Ad-Level Reports** | campaign ads, keyword by ad group, search terms by ad group |
| **Budget Orders** | list, get, create |
| **Geo Targeting** | search locations, get geo data, get/set campaign targeting |
| **Ads / Variations** | list, create, delete |
| **Creatives** | list creative sets, product page results, rejection reasons |
| **ACL / Users** | list ACLs, current user info |
| **App Search** | search apps, campaign eligibility, supported countries |
| **Optimization** | automated promote/block workflow with configurable thresholds |

## 🤖 Claude Code Integration

This CLI includes a `SKILL.md` file for use with [Claude Code](https://claude.ai/code). When loaded, Claude can manage your Apple Search Ads campaigns conversationally:

```
You: Add some category keywords for a photo editing app
Claude: [Runs asa keywords add "photo editor,image filter,picture effects" --type category]
```

## 📚 Documentation

- [Apple Search Ads Best Practices](https://ads.apple.com/app-store/best-practices/campaign-structure)
- [Apple Ads API Documentation](https://developer.apple.com/documentation/apple_ads)
- [SKILL.md](SKILL.md) — Full command reference for Claude Code
- [API Completion Plan](docs/API-COMPLETION-PLAN.md) — Implementation roadmap

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[MIT](LICENSE) © Cameron Ehrlich
