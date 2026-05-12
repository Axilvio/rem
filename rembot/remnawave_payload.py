from typing import Any


class RemnawavePayloadError(ValueError):
    pass


def unwrap_response(payload: Any) -> Any:
    if isinstance(payload, dict) and "response" in payload:
        return payload["response"]
    return payload


def extract_object(payload: Any, action: str) -> dict[str, Any]:
    response = unwrap_response(payload)
    if isinstance(response, dict):
        return response
    raise RemnawavePayloadError(f"Unexpected Remnawave API response while {action}")


def extract_internal_squad_uuids(payload: Any) -> list[str]:
    response = unwrap_response(payload)
    squads = response.get("internalSquads", []) if isinstance(response, dict) else []
    return [str(squad["uuid"]) for squad in squads if isinstance(squad, dict) and squad.get("uuid")]


def build_subscription_url(user: dict[str, Any], subscription_base_url: str | None) -> str | None:
    short_uuid = user.get("shortUuid") or user.get("short_uuid")
    if subscription_base_url and short_uuid:
        return f"{subscription_base_url.rstrip('/')}/{short_uuid}"
    url = user.get("subscriptionUrl") or user.get("subscription_url")
    return str(url) if url else None
