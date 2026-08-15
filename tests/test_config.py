"""Tests for configuration module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from asa_cli.config import (
    CAMPAIGN_STRUCTURE,
    CAMPAIGN_TYPE_NAMES,
    AppConfig,
    CampaignType,
    Credentials,
    MultiAppConfig,
    detect_campaign_type,
    get_active_app_config,
    get_app_slug,
    get_campaign_name,
    is_multi_app,
    load_app_config,
    load_credentials,
    load_multi_app_config,
    save_app_config,
    save_credentials,
    save_multi_app_config,
)


class TestCampaignNaming:
    """Tests for campaign name generation and detection."""

    def test_get_campaign_name_brand(self):
        """Test brand campaign name generation."""
        name = get_campaign_name(CampaignType.BRAND)
        assert name == "Brand"

    def test_get_campaign_name_category(self):
        """Test category campaign name generation."""
        name = get_campaign_name(CampaignType.CATEGORY)
        assert name == "Category"

    def test_get_campaign_name_competitor(self):
        """Test competitor campaign name generation."""
        name = get_campaign_name(CampaignType.COMPETITOR)
        assert name == "Competitor"

    def test_get_campaign_name_discovery(self):
        """Test discovery campaign name generation."""
        name = get_campaign_name(CampaignType.DISCOVERY)
        assert name == "Discovery"

    def test_all_campaign_types_have_names(self):
        """Test all campaign types have names defined."""
        for ctype in CampaignType:
            assert ctype in CAMPAIGN_TYPE_NAMES
            assert get_campaign_name(ctype) is not None

    def test_get_campaign_name_with_app_prefix(self):
        """Test campaign name with app name prefix (multi-app mode)."""
        name = get_campaign_name(CampaignType.BRAND, app_name="Stitch It")
        assert name == "StitchIt - Brand"

    def test_get_campaign_name_with_simple_app(self):
        """Test campaign name with simple app name."""
        name = get_campaign_name(CampaignType.DISCOVERY, app_name="ColorCub")
        assert name == "ColorCub - Discovery"

    def test_get_campaign_name_no_app_is_simple(self):
        """Test campaign name without app_name returns simple name."""
        name = get_campaign_name(CampaignType.CATEGORY)
        assert name == "Category"
        assert " - " not in name


class TestCampaignTypeDetection:
    """Tests for campaign type detection from names."""

    def test_detect_brand_campaign(self):
        """Test detecting brand campaign."""
        assert detect_campaign_type("Brand") == CampaignType.BRAND
        assert detect_campaign_type("My Brand Campaign") == CampaignType.BRAND
        assert detect_campaign_type("BRAND_US") == CampaignType.BRAND

    def test_detect_category_campaign(self):
        """Test detecting category campaign."""
        assert detect_campaign_type("Category") == CampaignType.CATEGORY
        assert detect_campaign_type("MyApp Category") == CampaignType.CATEGORY

    def test_detect_competitor_campaign(self):
        """Test detecting competitor campaign."""
        assert detect_campaign_type("Competitor") == CampaignType.COMPETITOR
        assert detect_campaign_type("competitor-us") == CampaignType.COMPETITOR

    def test_detect_discovery_campaign(self):
        """Test detecting discovery campaign."""
        assert detect_campaign_type("Discovery") == CampaignType.DISCOVERY
        assert detect_campaign_type("My Discovery Campaign") == CampaignType.DISCOVERY

    def test_detect_case_insensitive(self):
        """Test detection is case insensitive."""
        assert detect_campaign_type("BRAND") == CampaignType.BRAND
        assert detect_campaign_type("brand") == CampaignType.BRAND
        assert detect_campaign_type("BrAnD") == CampaignType.BRAND

    def test_detect_unknown_campaign(self):
        """Test unknown campaign returns None."""
        assert detect_campaign_type("Some Random Name") is None
        assert detect_campaign_type("Test Campaign") is None

    def test_detect_scoped_by_app_name(self):
        """Test detection scoped to specific app name."""
        # StitchIt - Brand should match for StitchIt
        assert detect_campaign_type("StitchIt - Brand", app_name="Stitch It") == CampaignType.BRAND
        # StitchIt - Brand should NOT match for ColorCub
        assert detect_campaign_type("StitchIt - Brand", app_name="ColorCub") is None

    def test_detect_scoped_accepts_own_app(self):
        """Test scoped detection accepts campaigns for the specified app."""
        assert detect_campaign_type("ColorCub - Discovery", app_name="ColorCub") == CampaignType.DISCOVERY
        assert detect_campaign_type("ColorCub - Category", app_name="ColorCub") == CampaignType.CATEGORY

    def test_detect_unscoped_matches_any(self):
        """Test unscoped detection matches any campaign with type keyword."""
        assert detect_campaign_type("StitchIt - Brand") == CampaignType.BRAND
        assert detect_campaign_type("ColorCub - Discovery") == CampaignType.DISCOVERY


class TestCampaignStructure:
    """Tests for campaign structure configuration."""

    def test_all_campaign_types_defined(self):
        """Test that all campaign types have structure defined."""
        for ctype in CampaignType:
            assert ctype in CAMPAIGN_STRUCTURE

    def test_brand_has_exact_ad_group(self):
        """Test brand campaign has exact match ad group."""
        config = CAMPAIGN_STRUCTURE[CampaignType.BRAND]
        assert len(config.ad_groups) == 1
        assert config.ad_groups[0].name == "Brand-Exact"
        assert config.ad_groups[0].search_match_enabled is False

    def test_discovery_has_two_ad_groups(self):
        """Test discovery campaign has broad and search match ad groups."""
        config = CAMPAIGN_STRUCTURE[CampaignType.DISCOVERY]
        assert len(config.ad_groups) == 2

        # Check for broad match ad group
        broad_ag = next((ag for ag in config.ad_groups if "Broad" in ag.name), None)
        assert broad_ag is not None
        assert broad_ag.search_match_enabled is False

        # Check for search match ad group
        search_ag = next((ag for ag in config.ad_groups if "SearchMatch" in ag.name), None)
        assert search_ag is not None
        assert search_ag.search_match_enabled is True


class TestCredentials:
    """Tests for credentials management."""

    def test_credentials_model(self):
        """Test credentials model validation."""
        creds = Credentials(
            org_id=123456,
            client_id="SEARCHADS.abc123",
            team_id="SEARCHADS.team456",
            key_id="key789",
            private_key_path="/path/to/key.pem",
        )
        assert creds.org_id == 123456
        assert creds.client_id == "SEARCHADS.abc123"

    def test_platform_credentials_do_not_require_legacy_org_id(self):
        creds = Credentials(
            ad_account_id="account-123",
            client_id="SEARCHADS.abc123",
            team_id="SEARCHADS.team456",
            key_id="key789",
            private_key_path="/path/to/key.pem",
        )

        assert creds.org_id is None
        assert creds.ad_account_id == "account-123"

    def test_save_and_load_credentials(self):
        """Test saving and loading credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            creds_file = config_dir / "credentials.json"

            creds = Credentials(
                org_id=123456,
                client_id="test_client",
                team_id="test_team",
                key_id="test_key",
                private_key_path="/path/to/key.pem",
            )

            # Save
            with patch("asa_cli.config.CREDENTIALS_FILE", creds_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_credentials(creds)

            # Verify file was created
            assert creds_file.exists()

            # Load
            with patch("asa_cli.config.CREDENTIALS_FILE", creds_file):
                loaded = load_credentials()

            assert loaded is not None
            assert loaded.org_id == 123456
            assert loaded.client_id == "test_client"


class TestAppConfig:
    """Tests for app configuration."""

    def test_app_config_model(self):
        """Test app config model validation."""
        config = AppConfig(
            app_id=123456789,
            app_name="TestApp",
            default_countries=["US", "CA"],
            default_bid=2.00,
        )
        assert config.app_id == 123456789
        assert config.app_name == "TestApp"
        assert "US" in config.default_countries

    def test_app_config_defaults(self):
        """Test app config default values."""
        config = AppConfig(app_id=123, app_name="TestApp")
        assert config.default_countries == ["US"]
        assert config.default_bid == 1.50

    def test_save_and_load_app_config(self):
        """Test saving and loading app config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = AppConfig(
                app_id=123456789,
                app_name="TestApp",
                default_countries=["US"],
                default_bid=2.50,
            )

            # Save
            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_app_config(config)

            # Verify file was created
            assert config_file.exists()

            # Load
            with patch("asa_cli.config.CONFIG_FILE", config_file):
                loaded = load_app_config()

            assert loaded is not None
            assert loaded.app_id == 123456789
            assert loaded.app_name == "TestApp"
            assert loaded.default_bid == 2.50


class TestAppSlug:
    """Tests for app slug derivation."""

    def test_slug_simple_name(self):
        assert get_app_slug("ColorCub") == "colorcub"

    def test_slug_name_with_spaces(self):
        assert get_app_slug("Stitch It") == "stitchit"

    def test_slug_name_with_hyphens(self):
        assert get_app_slug("Re-Shoot") == "reshoot"

    def test_slug_name_with_mixed(self):
        assert get_app_slug("How High!") == "howhigh"

    def test_slug_already_clean(self):
        assert get_app_slug("myapp") == "myapp"


class TestMultiAppConfig:
    """Tests for multi-app configuration."""

    def test_multi_app_model(self):
        """Test MultiAppConfig model."""
        config = MultiAppConfig(
            active_app="stitchit",
            apps={
                "stitchit": AppConfig(app_id=123, app_name="Stitch It"),
                "colorcub": AppConfig(app_id=456, app_name="ColorCub"),
            },
        )
        assert config.active_app == "stitchit"
        assert len(config.apps) == 2
        assert config.apps["stitchit"].app_id == 123

    def test_multi_app_empty(self):
        """Test empty MultiAppConfig."""
        config = MultiAppConfig()
        assert config.active_app is None
        assert config.apps == {}

    def test_save_and_load_round_trip(self):
        """Test saving and loading multi-app config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = MultiAppConfig(
                active_app="stitchit",
                apps={
                    "stitchit": AppConfig(app_id=123, app_name="Stitch It", default_bid=1.50),
                    "colorcub": AppConfig(app_id=456, app_name="ColorCub", default_bid=1.00),
                },
            )

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            assert config_file.exists()

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                loaded = load_multi_app_config()

            assert loaded.active_app == "stitchit"
            assert len(loaded.apps) == 2
            assert loaded.apps["stitchit"].app_id == 123
            assert loaded.apps["colorcub"].app_name == "ColorCub"

    def test_legacy_migration(self):
        """Test auto-migration from legacy single-app format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Write legacy format
            legacy_data = {
                "app_id": 123,
                "app_name": "Stitch It",
                "default_countries": ["US"],
                "default_bid": 1.50,
            }
            with open(config_file, "w") as f:
                json.dump(legacy_data, f)

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    loaded = load_multi_app_config()

            # Should have migrated
            assert loaded.active_app == "stitchit"
            assert "stitchit" in loaded.apps
            assert loaded.apps["stitchit"].app_id == 123
            assert loaded.apps["stitchit"].app_name == "Stitch It"

            # Verify file was rewritten in new format
            with open(config_file) as f:
                saved_data = json.load(f)
            assert "apps" in saved_data
            assert "active_app" in saved_data

    def test_active_app_resolution(self):
        """Test get_active_app_config resolves correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = MultiAppConfig(
                active_app="colorcub",
                apps={
                    "stitchit": AppConfig(app_id=123, app_name="Stitch It"),
                    "colorcub": AppConfig(app_id=456, app_name="ColorCub"),
                },
            )

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            # Without explicit slug, should return active app
            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config._current_app_slug", None):
                    result = get_active_app_config()
                    assert result is not None
                    assert result.app_name == "ColorCub"

            # With explicit slug, should return that app
            with patch("asa_cli.config.CONFIG_FILE", config_file):
                result = get_active_app_config(app_slug="stitchit")
                assert result is not None
                assert result.app_name == "Stitch It"

    def test_module_level_slug_override(self):
        """Test module-level _current_app_slug overrides active_app."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = MultiAppConfig(
                active_app="colorcub",
                apps={
                    "stitchit": AppConfig(app_id=123, app_name="Stitch It"),
                    "colorcub": AppConfig(app_id=456, app_name="ColorCub"),
                },
            )

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            # Set module-level slug
            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config._current_app_slug", "stitchit"):
                    result = get_active_app_config()
                    assert result is not None
                    assert result.app_name == "Stitch It"

    def test_single_app_returns_it_regardless(self):
        """Test single app is returned even without active_app set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = MultiAppConfig(
                active_app=None,
                apps={
                    "myapp": AppConfig(app_id=789, app_name="MyApp"),
                },
            )

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config._current_app_slug", None):
                    result = get_active_app_config()
                    assert result is not None
                    assert result.app_name == "MyApp"

    def test_is_multi_app(self):
        """Test is_multi_app returns correct values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            # Single app
            config = MultiAppConfig(
                active_app="myapp",
                apps={"myapp": AppConfig(app_id=123, app_name="MyApp")},
            )

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                assert is_multi_app() is False

            # Multiple apps
            config.apps["other"] = AppConfig(app_id=456, app_name="Other")

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_multi_app_config(config)

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                assert is_multi_app() is True

    def test_save_app_config_backward_compat(self):
        """Test save_app_config wraps into multi-app structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            config_file = config_dir / "config.json"

            config = AppConfig(app_id=123, app_name="TestApp", default_bid=2.00)

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config.CONFIG_DIR", config_dir):
                    save_app_config(config)

            # Should be saved in multi-app format
            with open(config_file) as f:
                data = json.load(f)

            assert "apps" in data
            assert "testapp" in data["apps"]
            assert data["active_app"] == "testapp"
            assert data["apps"]["testapp"]["app_id"] == 123

    def test_no_config_returns_none(self):
        """Test get_active_app_config returns None when no config exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "nonexistent.json"

            with patch("asa_cli.config.CONFIG_FILE", config_file):
                with patch("asa_cli.config._current_app_slug", None):
                    result = get_active_app_config()
                    assert result is None
