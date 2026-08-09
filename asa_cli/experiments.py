"""Small manifest model for Apple Ads custom-product-page experiments."""

# ruff: noqa: UP045 -- The package still supports Python 3.9.

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ExperimentAd(BaseModel):
    """An Apple Ads ad participating in an experiment."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    creative_id: int = Field(gt=0)
    ad_id: Optional[int] = Field(default=None, gt=0)
    initial_status: str = "PAUSED"

    @field_validator("initial_status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"ENABLED", "PAUSED"}:
            raise ValueError("initial_status must be ENABLED or PAUSED")
        return normalized


class CPPExperimentManifest(BaseModel):
    """Versioned link between an ASC product page and Apple Ads entities."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int
    experiment_id: str = Field(min_length=1)
    hypothesis: str = Field(min_length=1)
    adam_id: int = Field(gt=0)
    custom_product_page_id: str = Field(min_length=1)
    campaign_id: int = Field(gt=0)
    ad_group_id: int = Field(gt=0)
    treatment: ExperimentAd

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: int) -> int:
        if value != 1:
            raise ValueError("Only experiment manifest schema_version 1 is supported")
        return value


def load_experiment_manifest(path: Path) -> CPPExperimentManifest:
    """Load and validate a manifest with concise errors for CLI callers."""
    try:
        payload = json.loads(path.read_text())
        return CPPExperimentManifest.model_validate(payload)
    except OSError as exc:
        raise ValueError(f"Could not read experiment manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Experiment manifest is not valid JSON: {exc}") from exc
    except ValidationError as exc:
        raise ValueError(f"Experiment manifest is invalid: {exc}") from exc
