"""Configuration management for Apple Ads CLI."""

import json
import os
import re
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Prompt

console = Console()

CONFIG_DIR = Path.home() / ".asa-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


class CampaignType(str, Enum):
    """Manual App Store search-results keyword themes."""

    BRAND = "brand"
    CATEGORY = "category"
    COMPETITOR = "competitor"
    DISCOVERY = "discovery"


class MatchType(str, Enum):
    """Keyword match types."""

    EXACT = "EXACT"
    BROAD = "BROAD"


class AdGroupType(str, Enum):
    """Ad group types within campaigns."""

    EXACT = "exact"
    BROAD = "broad"
    SEARCH_MATCH = "search_match"


class AdGroupConfig(BaseModel):
    """Configuration for an ad group."""

    name: str
    match_type: Optional[MatchType] = None
    search_match_enabled: bool = False


class CampaignConfig(BaseModel):
    """Configuration for a campaign type."""

    name_suffix: str
    description: str
    ad_groups: list[AdGroupConfig]
    recommended_budget: float = 50.0


# Manual search-results themes; physical campaign grouping is caller-selected.
CAMPAIGN_STRUCTURE: dict[CampaignType, CampaignConfig] = {
    CampaignType.BRAND: CampaignConfig(
        name_suffix="Brand",
        description="Target keywords related to your app/company name",
        ad_groups=[
            AdGroupConfig(name="Brand-Exact", match_type=MatchType.EXACT, search_match_enabled=False)
        ],
        recommended_budget=50.0,
    ),
    CampaignType.CATEGORY: CampaignConfig(
        name_suffix="Category",
        description="Non-branded keywords describing app category/functionality",
        ad_groups=[
            AdGroupConfig(
                name="Category-Exact", match_type=MatchType.EXACT, search_match_enabled=False
            )
        ],
        recommended_budget=50.0,
    ),
    CampaignType.COMPETITOR: CampaignConfig(
        name_suffix="Competitor",
        description="Target competitor app brand terms",
        ad_groups=[
            AdGroupConfig(
                name="Competitor-Exact", match_type=MatchType.EXACT, search_match_enabled=False
            )
        ],
        recommended_budget=50.0,
    ),
    CampaignType.DISCOVERY: CampaignConfig(
        name_suffix="Discovery",
        description="Keyword mining and audience expansion",
        ad_groups=[
            AdGroupConfig(
                name="Discovery-Broad", match_type=MatchType.BROAD, search_match_enabled=False
            ),
            AdGroupConfig(name="Discovery-SearchMatch", match_type=None, search_match_enabled=True),
        ],
        recommended_budget=50.0,
    ),
}

# Simple campaign names (Apple's recommended types)
# These are detected by looking for the type name in the campaign name (case-insensitive)
CAMPAIGN_TYPE_NAMES = {
    CampaignType.BRAND: "Brand",
    CampaignType.CATEGORY: "Category",
    CampaignType.COMPETITOR: "Competitor",
    CampaignType.DISCOVERY: "Discovery",
}


class Credentials(BaseModel):
    """API credentials for Apple Ads."""

    org_id: Optional[int] = Field(
        None,
        description="Legacy Campaign Management API v5 organization ID",
    )
    ad_account_id: Optional[str] = Field(
        None,
        description="Apple Ads Platform API ad account ID",
    )
    client_id: str = Field(..., description="Client ID from Apple Ads API settings")
    team_id: str = Field(..., description="Team ID from Apple Ads API settings")
    key_id: str = Field(..., description="Key ID from Apple Ads API settings")
    private_key_path: str = Field(..., description="Path to private key PEM file")
    public_key_path: Optional[str] = Field(None, description="Path to public key PEM file")


class AppConfig(BaseModel):
    """Application configuration."""

    app_id: int = Field(..., description="Apple App ID (adam_id)")
    app_name: str = Field(..., description="App name for display")
    default_countries: list[str] = Field(default=["US"], description="Default target countries")
    default_bid: float = Field(default=1.50, description="Default keyword bid in USD")
    default_cpa_goal: Optional[float] = Field(None, description="Default CPA goal in USD")


class MultiAppConfig(BaseModel):
    """Multi-app configuration container."""

    active_app: Optional[str] = Field(None, description="Active app slug")
    apps: dict[str, AppConfig] = Field(default_factory=dict, description="App configs by slug")


# ---------------------------------------------------------------------------
# Module-level state for current app (set once in main.py callback)
# Safe for single-threaded CLI.
# ---------------------------------------------------------------------------
_current_app_slug: Optional[str] = None


def set_current_app(slug: Optional[str]) -> None:
    """Set the current app slug (called from --app flag in main.py callback)."""
    global _current_app_slug
    _current_app_slug = slug


def get_app_slug(app_name: str) -> str:
    """Derive a slug from an app name.

    Examples:
        "Stitch It" -> "stitchit"
        "ColorCub"  -> "colorcub"
        "How High"  -> "howhigh"
        "Re-Shoot"  -> "reshoot"
    """
    return re.sub(r"[^a-z0-9]", "", app_name.lower())


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_credentials() -> Optional[Credentials]:
    """Load credentials from config file."""
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        with open(CREDENTIALS_FILE) as f:
            data = json.load(f)
        return Credentials(**data)
    except (json.JSONDecodeError, ValueError) as e:
        console.print(f"[red]Error loading credentials: {e}[/red]")
        return None


def save_credentials(credentials: Credentials) -> None:
    """Save credentials to config file."""
    ensure_config_dir()
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials.model_dump(), f, indent=2)
    os.chmod(CREDENTIALS_FILE, 0o600)  # Restrict permissions
    console.print(f"[green]Credentials saved to {CREDENTIALS_FILE}[/green]")


# ---------------------------------------------------------------------------
# Multi-app config load / save with legacy migration
# ---------------------------------------------------------------------------

def load_multi_app_config() -> MultiAppConfig:
    """Load multi-app config from config file, migrating legacy format if needed.

    Legacy format (has 'app_id' at root, no 'apps' key):
        {"app_id": 123, "app_name": "Stitch It", ...}

    New format:
        {"active_app": "stitchit", "apps": {"stitchit": {...}}}

    Returns MultiAppConfig (may have empty apps dict if no config exists).
    """
    if not CONFIG_FILE.exists():
        return MultiAppConfig()

    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return MultiAppConfig()

    # Detect legacy format: has 'app_id' at root and no 'apps' key
    if "app_id" in data and "apps" not in data:
        app_config = AppConfig(**data)
        slug = get_app_slug(app_config.app_name)
        multi = MultiAppConfig(active_app=slug, apps={slug: app_config})
        # Auto-migrate: save in new format
        save_multi_app_config(multi)
        return multi

    # New format
    return MultiAppConfig(**data)


def save_multi_app_config(config: MultiAppConfig) -> None:
    """Save multi-app config to config file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def get_active_app_config(app_slug: Optional[str] = None) -> Optional[AppConfig]:
    """Resolve an app config by slug, or fall back to active_app.

    Priority:
    1. Explicit app_slug parameter
    2. Module-level _current_app_slug (set by --app flag)
    3. MultiAppConfig.active_app

    Returns None if no app is configured or slug not found.
    """
    multi = load_multi_app_config()

    if not multi.apps:
        return None

    slug = app_slug or _current_app_slug or multi.active_app

    if slug and slug in multi.apps:
        return multi.apps[slug]

    # If only one app and no slug specified, return it
    if len(multi.apps) == 1:
        return next(iter(multi.apps.values()))

    return None


def get_current_app_config() -> Optional[AppConfig]:
    """Get the app config for the current app (convenience wrapper)."""
    return get_active_app_config()


def is_multi_app() -> bool:
    """Return True if more than one app is configured."""
    multi = load_multi_app_config()
    return len(multi.apps) > 1


# ---------------------------------------------------------------------------
# Backward-compatible load/save wrappers
# ---------------------------------------------------------------------------

def load_app_config() -> Optional[AppConfig]:
    """Load app configuration from config file.

    Backward-compatible wrapper that returns the active app's config.
    """
    return get_active_app_config()


def save_app_config(config: AppConfig) -> None:
    """Save app configuration to config file.

    Backward-compatible wrapper that saves into the multi-app structure.
    """
    multi = load_multi_app_config()
    slug = get_app_slug(config.app_name)

    multi.apps[slug] = config
    if multi.active_app is None:
        multi.active_app = slug

    save_multi_app_config(multi)
    console.print(f"[green]Config saved to {CONFIG_FILE}[/green]")


# ---------------------------------------------------------------------------
# Campaign naming (with optional app prefix for multi-app)
# ---------------------------------------------------------------------------

def get_campaign_name(campaign_type: CampaignType, app_name: Optional[str] = None) -> str:
    """Get the campaign name for a type, optionally prefixed with app name.

    Single-app:  "Brand", "Category", etc.
    Multi-app:   "StitchIt - Brand", "ColorCub - Category", etc.

    When app_name is provided (multi-app mode), the name is prefixed.
    """
    type_name = CAMPAIGN_TYPE_NAMES[campaign_type]
    if app_name:
        # Remove spaces/special chars from app name for clean prefix
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", app_name)
        return f"{clean_name} - {type_name}"
    return type_name


def detect_campaign_type(name: str, app_name: Optional[str] = None) -> Optional[CampaignType]:
    """Detect campaign type from a campaign name (case-insensitive).

    When app_name is provided (multi-app scoping), also requires the app name
    prefix to be present in the campaign name.

    Returns the CampaignType or None if not detected.
    """
    name_lower = name.lower()

    # If app_name is provided, require it in the campaign name
    if app_name:
        clean_app = re.sub(r"[^a-z0-9]", "", app_name.lower())
        if clean_app not in re.sub(r"[^a-z0-9]", "", name_lower):
            return None

    for ctype, type_name in CAMPAIGN_TYPE_NAMES.items():
        if type_name.lower() in name_lower:
            return ctype
    return None


def parse_campaign_name(name: str, app_name: Optional[str] = None) -> Optional[tuple[str, CampaignType, list[str]]]:
    """Parse a campaign name to detect its type.

    This function provides backward compatibility. It now uses simple name detection.
    Returns (app_name, campaign_type, countries) or None if type not detected.

    The app_name and countries are placeholder values since we no longer encode them in the name.
    """
    ctype = detect_campaign_type(name, app_name=app_name)
    if ctype:
        # Return placeholder values for backward compatibility
        app_config = get_active_app_config()
        resolved_app_name = app_config.app_name if app_config else "App"
        countries = app_config.default_countries if app_config else ["US"]
        return (resolved_app_name, ctype, countries)
    return None


def prompt_for_credentials() -> Credentials:
    """Interactively prompt for API credentials."""
    console.print("\n[bold]Apple Ads API Credentials Setup[/bold]\n")
    console.print("You'll need to create API credentials in Apple Ads dashboard first.")
    console.print("See: https://ads.apple.com/help/campaigns/0022-use-the-campaign-management-api\n")

    org_id_input = Prompt.ask(
        "Organization ID (legacy API v5, optional)",
        default="",
        show_default=False,
    ).strip()
    org_id = int(org_id_input) if org_id_input else None
    ad_account_id = Prompt.ask(
        "Ad Account ID (Platform API v1, optional)",
        default="",
        show_default=False,
    ).strip()
    client_id = Prompt.ask("Client ID")
    team_id = Prompt.ask("Team ID")
    key_id = Prompt.ask("Key ID")
    private_key_path = Prompt.ask("Path to private key PEM file")

    # Expand user path
    private_key_path = os.path.expanduser(private_key_path)

    if not os.path.exists(private_key_path):
        console.print(f"[yellow]Warning: Private key file not found at {private_key_path}[/yellow]")

    return Credentials(
        org_id=org_id,
        ad_account_id=ad_account_id or None,
        client_id=client_id,
        team_id=team_id,
        key_id=key_id,
        private_key_path=private_key_path,
    )


def prompt_for_app_config() -> AppConfig:
    """Interactively prompt for app configuration."""
    console.print("\n[bold]App Configuration Setup[/bold]\n")

    app_id = int(Prompt.ask("Apple App ID (adam_id)", default="0"))
    app_name = Prompt.ask("App name (for display)")
    countries = Prompt.ask("Default target countries (comma-separated)", default="US")
    default_bid = float(Prompt.ask("Default keyword bid (USD)", default="1.50"))

    return AppConfig(
        app_id=app_id,
        app_name=app_name,
        default_countries=[c.strip().upper() for c in countries.split(",")],
        default_bid=default_bid,
    )
