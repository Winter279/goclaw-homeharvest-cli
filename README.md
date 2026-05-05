# goclaw-homeharvest-cli

CLI wrapper around [HomeHarvest](https://github.com/ZacharyHampton/HomeHarvest) — scrape **Realtor.com** real-estate listings with JSON-friendly output for AI agents (GoClaw, Claude Code, etc.).

> ⚠️ **US-only data.** HomeHarvest pulls from Realtor.com. Vietnam/Asia listings are not supported.

## Install

Requires **Python 3.10+** (the npm package shells out to a bundled Python script).

### Via npm (recommended)

```bash
npm install -g @winter279/goclaw-homeharvest-cli
```

The `postinstall` step auto-installs the Python `homeharvest` dep via `pip --user`. If your Python is PEP 668-locked (e.g. Homebrew), it falls back to `--break-system-packages`. To skip the auto-install, set `GOCLAW_HOMEHARVEST_SKIP_POSTINSTALL=1` and run `pip install homeharvest>=0.4.10` yourself (preferably inside a venv).

To point the shim at a specific Python binary:

```bash
export GOCLAW_HOMEHARVEST_PYTHON=/path/to/venv/bin/python
```

### Via pip (Python-only)

```bash
pip install git+https://github.com/Winter279/goclaw-homeharvest-cli
```

## Usage

```bash
goclaw-homeharvest scrape --location "San Diego, CA" --listing-type for_sale --past-days 7
```

### Common flags

| Flag | Description |
| --- | --- |
| `-l, --location` | ZIP, city, "city, state", full address, neighborhood, county, or state. **Required.** |
| `-t, --listing-type` | `for_sale`, `for_rent`, `sold`, `pending`, `off_market`, `new_community`, `other`, `ready_to_build`. Repeat flag for multiple. |
| `-p, --property-type` | `single_family`, `multi_family`, `condos`, `townhomes`, `land`, etc. Repeat for multiple. |
| `--radius` | Miles (only when `--location` is an address). |
| `--past-days` / `--past-hours` | Time-based filter. |
| `--date-from` / `--date-to` | `YYYY-MM-DD` range (both required together). |
| `--beds-min/max`, `--baths-min/max`, `--sqft-min/max`, `--price-min/max`, `--lot-sqft-min`, `--year-built-min/max` | Property filters. |
| `--sort-by` | `list_price`, `list_date`, `sqft`, `beds`, `baths`, `last_update_date`. |
| `--sort-direction` | `asc` or `desc`. |
| `--limit` | Cap result count. |
| `-o, --output` | `json` (default) or `csv`. |
| `--out-file` | Write to file instead of stdout. |
| `--fields` | Comma-separated subset of columns (json mode only). |

### Examples

Newest for-sale listings in last 24h, JSON to stdout:

```bash
goclaw-homeharvest scrape \
  -l "Austin, TX" \
  -t for_sale \
  --past-hours 24 \
  --sort-by list_date --sort-direction desc \
  --limit 20
```

Recent sold comps within 5 miles of an address, CSV file:

```bash
goclaw-homeharvest scrape \
  -l "1234 Main St, San Diego, CA 92104" \
  -t sold \
  --radius 5 \
  --past-days 90 \
  -o csv --out-file comps.csv
```

Trim to key fields for AI agent consumption:

```bash
goclaw-homeharvest scrape \
  -l 92104 -t for_sale --limit 10 \
  --fields list_price,beds,full_baths,sqft,property_url,formatted_address
```

## Use as a tool for an AI agent

Pipe JSON straight into your agent's tool runner:

```bash
goclaw-homeharvest scrape -l "Miami, FL" -t for_sale --past-days 3 --limit 50 \
  | jq '.results[] | {price: .list_price, beds, sqft, url: .property_url}'
```

## License

MIT
