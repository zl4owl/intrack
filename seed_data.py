from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from bson import ObjectId

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_handling import (
    add_donation,
    donors_collection,
    donations_collection,
    recipients_collection,
    register_donor,
    register_recipient,
)

DEFAULT_DONORS = [
    {
        "name": "FreshMart",
        "type": "supermarket",
        "contact": "hello@freshmart.test",
        "address": "12 Market Lane",
    },
    {
        "name": "GreenHarvest",
        "type": "farm",
        "contact": "info@greenharvest.test",
        "address": "89 Orchard Road",
    },
    {
        "name": "CityEats",
        "type": "restaurant",
        "contact": "contact@cityeats.test",
        "address": "5 Central Ave",
    },
    {
        "name": "BakersHub",
        "type": "bakery",
        "contact": "team@bakershub.test",
        "address": "42 Dough Street",
    },
]

DEFAULT_RECIPIENTS = [
    {
        "name": "Hope Foodbank",
        "type": "foodbank",
        "contact": "support@hopefoodbank.test",
        "address": "200 Shelter Way",
    },
    {
        "name": "River Shelter",
        "type": "shelter",
        "contact": "care@rivershelter.test",
        "address": "17 River Road",
    },
    {
        "name": "Community Pantry",
        "type": "community",
        "contact": "hello@pantry.test",
        "address": "77 Shared St",
    },
    {
        "name": "School Meals",
        "type": "school",
        "contact": "meals@school.test",
        "address": "1 Learning Way",
    },
]

ITEM_POOL = [
    ("apples", "kg", "produce"),
    ("bananas", "kg", "produce"),
    ("bread", "loaves", "bakery"),
    ("canned beans", "units", "pantry"),
    ("rice", "kg", "pantry"),
    ("milk", "litres", "dairy"),
    ("yogurt", "units", "dairy"),
    ("tomatoes", "kg", "produce"),
]

STATUS_CHOICES = ["available", "reserved", "picked_up", "distributed", "expired"]


def _seed_tag(tag: str) -> str:
    return tag.strip() or "seed"


def _random_item() -> Dict[str, str]:
    name, unit, category = random.choice(ITEM_POOL)
    quantity = random.randint(5, 120)
    expiry = datetime.now(timezone.utc) + timedelta(days=random.randint(2, 60))
    return {
        "name": name,
        "quantity": str(quantity),
        "unit": unit,
        "category": category,
        "expiry_date": expiry.date().isoformat(),
    }


def _seed_institutions(seed_tag: str) -> Dict[str, List[str]]:
    donor_ids: List[str] = []
    recipient_ids: List[str] = []

    for donor in DEFAULT_DONORS:
        donor_id = register_donor(
            donor["name"], donor["type"], donor["contact"], donor["address"]
        )
        donors_collection().update_one(
            {"_id": ObjectId(donor_id)}, {"$set": {"seed_tag": seed_tag}}
        )
        donor_ids.append(donor_id)

    for recipient in DEFAULT_RECIPIENTS:
        recipient_id = register_recipient(
            recipient["name"],
            recipient["type"],
            recipient["contact"],
            recipient["address"],
        )
        recipients_collection().update_one(
            {"_id": ObjectId(recipient_id)}, {"$set": {"seed_tag": seed_tag}}
        )
        recipient_ids.append(recipient_id)

    return {"donors": donor_ids, "recipients": recipient_ids}


def _seed_donations(
    donor_ids: List[str],
    recipient_ids: List[str],
    seed_tag: str,
    min_count: int,
    max_count: int,
) -> List[str]:
    donation_ids: List[str] = []
    count = random.randint(min_count, max_count)
    for _ in range(count):
        items = [_random_item() for _ in range(random.randint(1, 4))]
        donor_id = random.choice(donor_ids)
        recipient_id = random.choice(recipient_ids) if recipient_ids else None
        status = random.choice(STATUS_CHOICES)
        donation_id = add_donation(
            donor_id,
            items,
            recipient_id=recipient_id,
            status=status,
        )
        donations_collection().update_one(
            {"_id": ObjectId(donation_id)}, {"$set": {"seed_tag": seed_tag}}
        )
        donation_ids.append(donation_id)
    return donation_ids


def _delete_seeded(seed_tag: str) -> Dict[str, int]:
    donor_result = donors_collection().delete_many({"seed_tag": seed_tag})
    recipient_result = recipients_collection().delete_many({"seed_tag": seed_tag})
    donation_result = donations_collection().delete_many({"seed_tag": seed_tag})
    return {
        "donors": donor_result.deleted_count,
        "recipients": recipient_result.deleted_count,
        "donations": donation_result.deleted_count,
    }


def _clear_db() -> Dict[str, int]:
    donors_result = donors_collection().delete_many({})
    recipients_result = recipients_collection().delete_many({})
    donations_result = donations_collection().delete_many({})
    return {
        "donors": donors_result.deleted_count,
        "recipients": recipients_result.deleted_count,
        "donations": donations_result.deleted_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed the Intrack database with demo data or clean it up."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--delete-seeded",
        action="store_true",
        help="Delete only the demo data created with this tool.",
    )
    group.add_argument(
        "--clear-db",
        action="store_true",
        help="Delete all donors, recipients, and donations.",
    )
    parser.add_argument(
        "--seed-tag",
        default="seed",
        help="Tag used to identify demo records for deletion.",
    )
    parser.add_argument(
        "--donations-min",
        type=int,
        default=8,
        help="Minimum number of demo donations to create.",
    )
    parser.add_argument(
        "--donations-max",
        type=int,
        default=16,
        help="Maximum number of demo donations to create.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    seed_tag = _seed_tag(args.seed_tag)

    if args.clear_db:
        results = _clear_db()
        print(
            f"Cleared donors={results['donors']}, recipients={results['recipients']}, "
            f"donations={results['donations']}"
        )
        return 0

    if args.delete_seeded:
        results = _delete_seeded(seed_tag)
        print(
            f"Deleted donors={results['donors']}, recipients={results['recipients']}, "
            f"donations={results['donations']}"
        )
        return 0

    if args.donations_min < 0 or args.donations_max < 0:
        raise SystemExit("Donation counts must be >= 0")
    if args.donations_min > args.donations_max:
        raise SystemExit("--donations-min must be <= --donations-max")

    ids = _seed_institutions(seed_tag)
    donation_ids = _seed_donations(
        ids["donors"],
        ids["recipients"],
        seed_tag,
        args.donations_min,
        args.donations_max,
    )
    print(
        f"Seeded donors={len(ids['donors'])}, recipients={len(ids['recipients'])}, "
        f"donations={len(donation_ids)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

