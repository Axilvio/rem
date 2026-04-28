from pydantic import BaseModel


class RoutingProfile(BaseModel):
    name: str
    entry_inbound_tag: str
    exit_outbound_tag: str
    fallback_outbound_tag: str
