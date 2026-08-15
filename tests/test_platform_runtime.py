"""Contract tests for the shared Apple Ads Platform SDK runtime."""

import json
from datetime import date
from types import SimpleNamespace
from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError

from asa_cli.config import Credentials
from asa_cli.platform.client import (
    PlatformConfigurationError,
    _deserialize_with_live_response_compatibility,
    build_platform_api,
    context_header,
    resolve_ad_account_id,
)
from asa_cli.platform.runtime import PlatformAPIError, invoke, read_json_payload, serialize_response


def credentials(ad_account_id="123456"):
    return Credentials(
        org_id=987,
        ad_account_id=ad_account_id,
        client_id="client",
        team_id="team",
        key_id="key",
        private_key_path="/tmp/private-key.pem",
    )


class FakeAPI:
    def __init__(self):
        self.calls = []

    def campaigns_id_get(self, **kwargs):
        self.calls.append(kwargs)
        return {"result": {"id": kwargs["id"]}}


def test_required_context_uses_ad_account_and_never_org_id():
    api = FakeAPI()

    result = invoke(
        "campaigns_id_get",
        arguments={"id": "42"},
        credentials=credentials(),
        api=api,
    )

    assert result == {"result": {"id": "42"}}
    assert api.calls == [{"id": "42", "x_ap_context": "adAccountId=123456;"}]


def test_explicit_account_overrides_saved_account():
    api = FakeAPI()

    invoke(
        "campaigns_id_get",
        arguments={"id": "42"},
        credentials=credentials(),
        ad_account_id="999",
        api=api,
    )

    assert api.calls[0]["x_ap_context"] == "adAccountId=999;"


def test_missing_account_fails_without_using_legacy_org(monkeypatch):
    monkeypatch.delenv("ASA_AD_ACCOUNT_ID", raising=False)

    with pytest.raises(PlatformConfigurationError, match="ad account ID"):
        resolve_ad_account_id(credentials(ad_account_id=None))


@pytest.mark.parametrize("account_id", ["12;admin", "a=b", "line\nbreak", "line\rbreak"])
def test_account_context_rejects_header_delimiters(account_id):
    with pytest.raises(PlatformConfigurationError, match="invalid characters"):
        context_header(credentials(), account_id)


def test_invoke_normalizes_missing_platform_configuration(monkeypatch):
    monkeypatch.delenv("ASA_AD_ACCOUNT_ID", raising=False)

    with pytest.raises(PlatformAPIError, match="ad account ID"):
        invoke(
            "campaigns_id_get",
            arguments={"id": "42"},
            credentials=credentials(ad_account_id=None),
            api=FakeAPI(),
        )


def test_no_context_operation_does_not_add_header():
    api = FakeAPI()

    invoke(
        "campaigns_id_get",
        arguments={"id": "42"},
        context="none",
        credentials=credentials(),
        api=api,
    )

    assert api.calls == [{"id": "42"}]


def test_optional_context_loads_saved_account_for_normal_cli_calls(monkeypatch):
    monkeypatch.setattr(
        "asa_cli.platform.client.load_credentials",
        lambda: credentials(ad_account_id="saved-123"),
    )
    api = FakeAPI()

    invoke(
        "campaigns_id_get",
        arguments={"id": "42"},
        context="optional",
        api=api,
    )

    assert api.calls == [{"id": "42", "x_ap_context": "adAccountId=saved-123;"}]


def test_read_json_payload_supports_file_and_reports_invalid_json(tmp_path):
    request = tmp_path / "request.json"
    request.write_text('{"filters": []}', encoding="utf-8")
    assert read_json_payload(request) == {"filters": []}

    request.write_text("not-json", encoding="utf-8")
    with pytest.raises(PlatformAPIError, match="Invalid JSON"):
        read_json_payload(request)


class ResponseModel(BaseModel):
    created: date
    identifier: UUID


def test_serialize_response_handles_pydantic_dates_and_uuids():
    value = ResponseModel(
        created=date(2026, 8, 14),
        identifier=UUID("12345678-1234-5678-1234-567812345678"),
    )

    assert serialize_response(value) == {
        "created": "2026-08-14",
        "identifier": "12345678-1234-5678-1234-567812345678",
    }


def test_serialize_response_flattens_generated_sdk_additional_properties():
    from apple_ads_platform.models.campaign_query_response import CampaignQueryResponse

    value = CampaignQueryResponse(
        result=[],
        additional_properties={"futureField": "future-value"},
    )

    assert serialize_response(value) == {
        "result": [],
        "futureField": "future-value",
    }


@pytest.mark.parametrize(
    ("response_type", "payload"),
    [
        (
            "AppsKeywordReportResponse",
            {
                "result": {
                    "rows": [
                        {
                            "metadata": {
                                "id": 123,
                                "text": "long screenshot",
                                "status": "ENABLED",
                            }
                        }
                    ]
                }
            },
        ),
        (
            "AppsSearchTermReportResponse",
            {
                "result": {
                    "rows": [
                        {
                            "metadata": {
                                "searchTermText": "long screenshot",
                                "keyword": {
                                    "id": 123,
                                    "text": "long screenshot",
                                    "status": "ENABLED",
                                },
                            }
                        }
                    ]
                }
            },
        ),
        (
            "ImpressionShareQueryResponse",
            {
                "result": {
                    "rows": [
                        {
                            "promotedObjectId": 554594252,
                            "searchTerm": "long screenshot",
                        }
                    ]
                }
            },
        ),
    ],
)
def test_confirmed_live_sdk_response_mismatches_are_preserved(response_type, payload):
    from apple_ads_platform.api_client import ApiClient

    response = SimpleNamespace(
        data=json.dumps(payload).encode(),
        status=200,
        headers={"content-type": "application/json"},
    )
    original = ApiClient().response_deserialize

    result = _deserialize_with_live_response_compatibility(
        original,
        response_data=response,
        response_types_map={"200": response_type},
    )

    assert result.data == payload


def test_build_platform_api_installs_compatibility_and_malformed_json_fails_closed(
    monkeypatch,
):
    from apple_ads_platform.api_client import ApiClient

    api = SimpleNamespace(api_client=ApiClient())

    class FakeBuilder:
        def build(self):
            return api

    monkeypatch.setattr(
        "apple_ads_platform.builder.AppleAdsClientBuilder.from_private_key_path",
        lambda *_args: FakeBuilder(),
    )

    built = build_platform_api(credentials())
    payload = {
        "result": {
            "rows": [
                {
                    "metadata": {
                        "id": 123,
                        "text": "long screenshot",
                        "status": "ENABLED",
                    }
                }
            ]
        }
    }
    valid_response = SimpleNamespace(
        data=json.dumps(payload).encode(),
        status=200,
        headers={"content-type": "application/json"},
    )
    result = built.api_client.response_deserialize(
        response_data=valid_response,
        response_types_map={"200": "AppsKeywordReportResponse"},
    )

    assert result.data == payload

    malformed_response = SimpleNamespace(
        data=b"{not-json",
        status=200,
        headers={"content-type": "application/json"},
    )
    with pytest.raises(json.JSONDecodeError):
        built.api_client.response_deserialize(
            response_data=malformed_response,
            response_types_map={"200": "AppsKeywordReportResponse"},
        )

    unsupported_payload = {
        "result": {
            "rows": [
                {
                    "metadata": {
                        "id": 123,
                        "text": "long screenshot",
                        "status": "FUTURE_VALUE",
                    }
                }
            ]
        }
    }
    unsupported_response = SimpleNamespace(
        data=json.dumps(unsupported_payload).encode(),
        status=200,
        headers={"content-type": "application/json"},
    )
    with pytest.raises(ValidationError):
        built.api_client.response_deserialize(
            response_data=unsupported_response,
            response_types_map={"200": "AppsKeywordReportResponse"},
        )


def test_unrelated_sdk_validation_error_is_not_bypassed():
    response = SimpleNamespace(
        data=b'{"result":{}}',
        status=200,
        headers={"content-type": "application/json"},
    )

    def invalid_response(**_kwargs):
        class ExpectedInteger(BaseModel):
            count: int

        ExpectedInteger.model_validate({"count": "not-an-integer"})

    with pytest.raises(ValidationError):
        _deserialize_with_live_response_compatibility(
            invalid_response,
            response_data=response,
            response_types_map={"200": "AppsKeywordReportResponse"},
        )


def test_sdk_error_is_normalized_with_structured_body():
    class SDKFailureError(Exception):
        status = 400
        reason = "Bad Request"
        body = '{"error":{"code":"INVALID_VALUE"}}'

    class BrokenAPI:
        def campaigns_id_get(self, **kwargs):
            raise SDKFailureError()

    with pytest.raises(PlatformAPIError) as raised:
        invoke(
            "campaigns_id_get",
            arguments={"id": "42"},
            credentials=credentials(),
            api=BrokenAPI(),
        )

    assert raised.value.status == 400
    assert raised.value.body == {"error": {"code": "INVALID_VALUE"}}


def test_sdk_error_without_reason_preserves_exception_message():
    class SDKValidationError(Exception):
        pass

    class BrokenAPI:
        def campaigns_id_get(self, **kwargs):
            raise SDKValidationError("id must be numeric")

    with pytest.raises(PlatformAPIError, match="id must be numeric"):
        invoke(
            "campaigns_id_get",
            arguments={"id": "bad"},
            credentials=credentials(),
            api=BrokenAPI(),
        )


def test_builder_errors_are_normalized(monkeypatch):
    class BuilderError(Exception):
        pass

    monkeypatch.setattr(
        "apple_ads_platform.builder.AppleAdsClientBuilder.from_private_key_path",
        lambda *args, **kwargs: (_ for _ in ()).throw(BuilderError("missing PEM")),
    )

    with pytest.raises(PlatformConfigurationError, match="missing PEM"):
        build_platform_api(credentials())
