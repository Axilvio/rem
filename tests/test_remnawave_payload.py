import pytest

from rembot.remnawave_payload import (
    RemnawavePayloadError,
    build_subscription_url,
    extract_internal_squad_uuids,
    extract_object,
    unwrap_response,
)


def test_unwrap_response_supports_remnawave_envelope() -> None:
    assert unwrap_response({"response": {"uuid": "u1"}}) == {"uuid": "u1"}


def test_extract_object_rejects_unexpected_payload() -> None:
    with pytest.raises(RemnawavePayloadError):
        extract_object(["not", "an", "object"], "testing")


def test_extract_internal_squad_uuids_from_enveloped_payload() -> None:
    payload = {
        "response": {
            "internalSquads": [
                {"uuid": "first"},
                {"name": "without uuid"},
                {"uuid": "second"},
            ]
        }
    }
    assert extract_internal_squad_uuids(payload) == ["first", "second"]


def test_build_subscription_url_prefers_short_uuid() -> None:
    user = {"shortUuid": "abc", "subscriptionUrl": "https://panel.example/full"}
    assert build_subscription_url(user, "https://sub.example/") == "https://sub.example/abc"


def test_build_subscription_url_falls_back_to_existing_url() -> None:
    user = {"subscription_url": "https://panel.example/sub/abc"}
    assert build_subscription_url(user, None) == "https://panel.example/sub/abc"
