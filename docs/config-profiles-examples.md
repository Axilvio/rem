# Config Profiles examples

## 1. Reality Bridge Entry (RU)
```json
{
  "inbounds": [{"tag":"VLESS_REALITY_IN","port":443,"protocol":"vless","settings":{"clients":[]},"streamSettings":{"network":"tcp","security":"reality"}}],
  "outbounds": [
    {"tag":"BRIDGE_TO_DE","protocol":"shadowsocks","settings":{"servers":[{"address":"de-exit.example.net","port":9999,"method":"chacha20-ietf-poly1305","password":"bridge-password"}]}},
    {"tag":"DIRECT","protocol":"freedom"},
    {"tag":"BLOCK","protocol":"blackhole"}
  ],
  "routing":{"rules":[
    {"domain":["geosite:category-ru"],"outboundTag":"DIRECT"},
    {"ip":["geoip:ru"],"outboundTag":"DIRECT"},
    {"outboundTag":"BRIDGE_TO_DE","network":"tcp,udp"}
  ]}
}
```

## 2. Direct Exit (DE)
```json
{
  "inbounds": [{"tag":"BRIDGE_DE_IN","port":9999,"protocol":"shadowsocks","settings":{"clients":[],"method":"chacha20-ietf-poly1305"}}],
  "outbounds": [{"tag":"DIRECT","protocol":"freedom"},{"tag":"BLOCK","protocol":"blackhole"}],
  "routing":{"rules":[]}
}
```

## 3. Fallback profile (WS/gRPC TLS + Trojan)
```json
{
  "inbounds":[{"tag":"WS_TLS_IN","port":8443,"protocol":"vless","settings":{"clients":[]},"streamSettings":{"network":"ws","security":"tls"}},{"tag":"TROJAN_IN","port":9443,"protocol":"trojan","settings":{"clients":[]}}],
  "outbounds":[{"tag":"DIRECT","protocol":"freedom"}],
  "routing":{"rules":[]}
}
```
