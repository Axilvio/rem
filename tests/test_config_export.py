from bot.app.services.config_export import ConfigExportService


def test_config_bundle_contains_all_clients() -> None:
    service = ConfigExportService()
    bundle = service.build_bundle("https://sub.example.com/user1", mode="bridge")
    assert bundle.v2rayng.startswith("https://")
    assert "mode=bridge" in bundle.v2rayng
    assert bundle.hiddify.startswith("hiddify://")
    assert "nekobox://" in bundle.nekobox
    assert "sing-box://" in bundle.singbox
    assert "clash://" in bundle.clash
