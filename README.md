# kenzy-hass

**Kenzy as a Home Assistant conversation agent** — talk to your household's
voice assistant from the HA companion app (phone, tablet, watch) through
Assist, with the same identity, memory, and skills you get by voice at home.

This is the *second front door*: your kenzy-server stays the brain. The
integration maps your HA login to the person Kenzy knows (the People page's
"HA person" link), relays each conversation turn to the server's `/assist`
channel, and speaks the reply. Household members Kenzy recognizes get their
memory and personalized skills; anyone else gets safe, gated answers — exactly
like an unrecognized voice in the kitchen.

## Requirements

- A running [Kenzy](https://docs.kenzy.ai) server (v4+) reachable from your
  Home Assistant instance
- Home Assistant 2025.1 or newer
- Your household members mapped to their HA person entities on Kenzy's
  dashboard (People → open a person → HA person)

## Install

**HACS** (recommended): add this repository as a custom repository
(Integrations), install **Kenzy**, restart Home Assistant.

Then: *Settings → Devices & Services → Add Integration → Kenzy* and enter:

| Field | Value |
|---|---|
| Host / Port | Your kenzy-server (port `8765` by default) |
| Fleet token | From the Kenzy dashboard's Settings page (leave empty if auth is disabled) |
| Use TLS | On for a TLS-enabled server (the default posture since Kenzy 3.11) |
| Verify TLS | Off for self-signed certificates (the LAN default) |

Finally, pick Kenzy as the conversation agent in *Settings → Voice assistants*.

## Kenzy's voice and ears (optional, recommended)

Kenzy 4.0+ can also be your pipeline's **text-to-speech and speech-to-text**,
so a voice turn from the companion app is Kenzy end-to-end — her STT hears
you, her brain answers, and the reply is spoken in her actual voice.

1. On the Kenzy side, enable the Wyoming listeners (dashboard → Services →
   tts / stt, or the service configs): `wyoming.enabled: true`. Defaults:
   TTS on port `10200`, STT on `10300`. The listeners follow the service
   bind — open the services to the LAN (`KENZY_BIND=0.0.0.0` /
   `--listen-all`) if HA runs on another host.
2. In HA: *Add integration → Wyoming Protocol*, once for each port. Both
   appear as **kenzy**.
3. In your voice assistant's pipeline, pick kenzy for Speech-to-text and
   Text-to-speech alongside the Kenzy conversation agent.

## Privacy & security

- The fleet token is proven by an HMAC signature — it never travels the wire.
- Identity, memory tiers, and skill gating are enforced **server-side**; this
  integration only ever sees the reply text.
- An HA user not mapped to a Kenzy person is served fail-closed: no memory
  reads or writes, no gated skills.
