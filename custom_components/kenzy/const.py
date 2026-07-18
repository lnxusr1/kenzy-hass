"""Constants for the Kenzy integration."""

DOMAIN = "kenzy"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"
CONF_USE_TLS = "use_tls"
CONF_VERIFY_TLS = "verify_tls"

DEFAULT_PORT = 8765  # the kenzy-server WebSocket port (its always-on HTTP hook)
DEFAULT_USE_TLS = True  # fresh Kenzy installs enable TLS by default (3.11+)
DEFAULT_VERIFY_TLS = False  # self-signed LAN posture — encrypted, unverified
