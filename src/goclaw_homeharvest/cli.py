"""CLI entrypoint — wraps `homeharvest.scrape_property` with JSON-friendly output."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from homeharvest import scrape_property

from . import __version__

LISTING_TYPES = [
    "for_sale",
    "for_rent",
    "sold",
    "pending",
    "off_market",
    "new_community",
    "other",
    "ready_to_build",
]

PROPERTY_TYPES = [
    "single_family",
    "multi_family",
    "condos",
    "condo_townhome_rowhome_coop",
    "condo_townhome",
    "townhomes",
    "duplex_triplex",
    "farm",
    "land",
    "mobile",
]

SORT_FIELDS = ["list_price", "list_date", "sqft", "beds", "baths", "last_update_date"]


def _json_default(obj: Any) -> Any:
    """JSON encoder fallback for pandas/numpy/datetime/Decimal."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="goclaw-homeharvest",
        description="Scrape Realtor.com listings via HomeHarvest. JSON-friendly for AI agents.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Scrape property listings")
    scrape.add_argument(
        "-l", "--location", required=True,
        help="ZIP, city, 'city, state', address, neighborhood, county, or state",
    )
    scrape.add_argument(
        "-t", "--listing-type", action="append", choices=LISTING_TYPES,
        help="Listing type (repeat flag for multiple). Default: common types.",
    )
    scrape.add_argument(
        "-p", "--property-type", action="append", choices=PROPERTY_TYPES,
        help="Property type filter (repeat flag for multiple).",
    )
    scrape.add_argument("--radius", type=float, help="Radius in miles (only when location is an address).")
    scrape.add_argument("--past-days", type=int, help="Filter by listings/sales in last N days.")
    scrape.add_argument("--past-hours", type=int, help="Filter by last N hours (more precise).")
    scrape.add_argument("--date-from", help="Start date YYYY-MM-DD (requires --date-to).")
    scrape.add_argument("--date-to", help="End date YYYY-MM-DD (requires --date-from).")
    scrape.add_argument("--beds-min", type=int)
    scrape.add_argument("--beds-max", type=int)
    scrape.add_argument("--baths-min", type=float)
    scrape.add_argument("--baths-max", type=float)
    scrape.add_argument("--sqft-min", type=int)
    scrape.add_argument("--sqft-max", type=int)
    scrape.add_argument("--price-min", type=int)
    scrape.add_argument("--price-max", type=int)
    scrape.add_argument("--lot-sqft-min", type=int)
    scrape.add_argument("--year-built-min", type=int)
    scrape.add_argument("--year-built-max", type=int)
    scrape.add_argument("--sort-by", choices=SORT_FIELDS)
    scrape.add_argument("--sort-direction", choices=["asc", "desc"])
    scrape.add_argument("--limit", type=int, help="Cap number of results.")
    scrape.add_argument(
        "-o", "--output", choices=["json", "csv"], default="json",
        help="Output format (default: json to stdout).",
    )
    scrape.add_argument("--out-file", help="Write to file instead of stdout.")
    scrape.add_argument(
        "--fields", help="Comma-separated subset of columns to keep (json only).",
    )

    return parser


def _scrape_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Map argparse namespace → scrape_property kwargs (drop None values)."""
    mapping = {
        "location": args.location,
        "listing_type": args.listing_type,
        "property_type": args.property_type,
        "radius": args.radius,
        "past_days": args.past_days,
        "past_hours": args.past_hours,
        "date_from": args.date_from,
        "date_to": args.date_to,
        "beds_min": args.beds_min,
        "beds_max": args.beds_max,
        "baths_min": args.baths_min,
        "baths_max": args.baths_max,
        "sqft_min": args.sqft_min,
        "sqft_max": args.sqft_max,
        "price_min": args.price_min,
        "price_max": args.price_max,
        "lot_sqft_min": args.lot_sqft_min,
        "year_built_min": args.year_built_min,
        "year_built_max": args.year_built_max,
        "sort_by": args.sort_by,
        "sort_direction": args.sort_direction,
        "limit": args.limit,
    }
    return {k: v for k, v in mapping.items() if v is not None}


def _emit(df, args: argparse.Namespace) -> None:
    """Write DataFrame as JSON or CSV to file or stdout."""
    if args.fields and args.output == "json":
        keep = [c.strip() for c in args.fields.split(",") if c.strip()]
        existing = [c for c in keep if c in df.columns]
        df = df[existing]

    if args.output == "csv":
        if args.out_file:
            df.to_csv(args.out_file, index=False)
        else:
            df.to_csv(sys.stdout, index=False)
        return

    records = df.to_dict(orient="records")
    payload = {"count": len(records), "results": records}
    text = json.dumps(payload, default=_json_default, ensure_ascii=False, indent=2)
    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text + "\n")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "scrape":
        try:
            df = scrape_property(**_scrape_kwargs(args))
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        _emit(df, args)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
