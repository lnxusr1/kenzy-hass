# Brand assets for brands.home-assistant.io

Home Assistant does **not** read integration icons from the component — the
tile on *Devices & Services* is fetched from the central
[home-assistant/brands](https://github.com/home-assistant/brands) repo. Until
our folder is merged there, HA shows the generic puzzle-piece icon.

The `kenzy/` folder here is the ready-to-submit payload (icon rendered from
the dashboard's `favicon.svg` — petrol tile, golden K; logo is the site
wordmark):

| File | Size | Note |
|---|---|---|
| `icon.png` | 256×256 | required |
| `icon@2x.png` | 512×512 | hiDPI variant |
| `logo.png` | 500×155 | optional wordmark |

## To submit

1. Fork `home-assistant/brands` on GitHub.
2. Copy `kenzy/` to `custom_integrations/kenzy/` in the fork
   (the folder name must match the integration `domain`).
3. Open a PR titled "Add kenzy (custom integration)".

Once merged, icons appear at
`https://brands.home-assistant.io/kenzy/icon.png` and HA picks them up
automatically (no integration release needed; browsers may cache the old
placeholder for a while).
