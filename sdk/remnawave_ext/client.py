from dataclasses import dataclass

from remnawave import RemnawaveSDK


@dataclass(slots=True)
class RemnawaveClientFactory:
    base_url: str
    token: str

    def create(self) -> RemnawaveSDK:
        return RemnawaveSDK(base_url=self.base_url, token=self.token)
