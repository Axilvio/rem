from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote


@dataclass(slots=True)
class ClientConfigBundle:
    v2rayng: str
    hiddify: str
    nekobox: str
    singbox: str
    clash: str


class ConfigExportService:
    def build_bundle(self, subscription_url: str, mode: str = "auto") -> ClientConfigBundle:
        url_with_mode = f"{subscription_url}?mode={mode}"
        encoded = quote(url_with_mode, safe="")
        return ClientConfigBundle(
            v2rayng=url_with_mode,
            hiddify=f"hiddify://import/{encoded}",
            nekobox=f"nekobox://add?url={encoded}",
            singbox=f"sing-box://import-remote-profile?url={encoded}",
            clash=f"clash://install-config?url={encoded}",
        )
