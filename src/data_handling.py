from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
import re

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId

# Connection defaults for central database
DEFAULT_MONGODB_URI = (
    "mongodb+srv://nova:2oyIpZLPfJMysdKI@cluster0.gp3j6cm.mongodb.net/?appName=Cluster0"
)
DEFAULT_DB_NAME = "food_donations"

# Cached client/database to avoid reconnect churn
_client_cache: Optional[MongoClient] = None
_db_cache: Optional[Database] = None


# Returns a cached Mongo client, with env override
def get_client() -> MongoClient:
    """Return a cached Mongo client; allow env override for local testing."""
    global _client_cache
    if _client_cache is None:
        uri = os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI)
        _client_cache = MongoClient(uri)
    return _client_cache


# Returns the central donations database
def get_db() -> Database:
    """Return the central donations database."""
    global _db_cache
    if _db_cache is None:
        db_name = os.getenv("MONGODB_DB", DEFAULT_DB_NAME)
        _db_cache = get_client()[db_name]
    return _db_cache


# Collection accessors
def donors_collection() -> Collection:
    return get_db()["donors"]


def recipients_collection() -> Collection:
    return get_db()["recipients"]


def donations_collection() -> Collection:
    return get_db()["donations"]


# ---- Pure helpers for validation / tests ----

# Normalizes item names for consistent storage/search
def normalize_item_name(name: str) -> str:
    return " ".join(name.strip().split()).lower()


# Validates dates and normalizes to ISO YYYY-MM-DD
def parse_iso_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    # Validate and normalize to YYYY-MM-DD
    parsed = datetime.strptime(value, "%Y-%m-%d").date()
    return parsed.isoformat()


# Builds a normalized donation document for storage
def build_donation_doc(
    donor_id: str,
    items: Iterable[Dict[str, Any]],
    recipient_id: Optional[str] = None,
    status: str = "available",
) -> Dict[str, Any]:
    normalized_items: List[Dict[str, Any]] = []
    for item in items:
        normalized_items.append(
            {
                "name": normalize_item_name(item["name"]),
                "quantity": float(item["quantity"]),
                "unit": item.get("unit", "units"),
                "category": item.get("category"),
                "expiry_date": parse_iso_date(item.get("expiry_date")),
            }
        )
    return {
        "donor_id": donor_id,
        "recipient_id": recipient_id,
        "items": normalized_items,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# ---- CRUD operations ----

# Inserts a donor record and returns its id
def register_donor(
    name: str,
    donor_type: str,
    contact: str,
    address: Optional[str],
) -> str:
    doc = {
        "name": name.strip(),
        "type": donor_type.strip().lower(),
        "contact": contact.strip(),
        "address": (address or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    result = donors_collection().insert_one(doc)
    return str(result.inserted_id)


# Inserts a recipient record and returns its id
def register_recipient(
    name: str,
    recipient_type: str,
    contact: str,
    address: Optional[str],
) -> str:
    doc = {
        "name": name.strip(),
        "type": recipient_type.strip().lower(),
        "contact": contact.strip(),
        "address": (address or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    result = recipients_collection().insert_one(doc)
    return str(result.inserted_id)


# Inserts a donation record and returns its id
def add_donation(
    donor_id: str,
    items: Iterable[Dict[str, Any]],
    recipient_id: Optional[str] = None,
    status: str = "available",
) -> str:
    doc = build_donation_doc(donor_id, items, recipient_id=recipient_id, status=status)
    result = donations_collection().insert_one(doc)
    return str(result.inserted_id)


# Updates donation status by id
def update_donation_status(donation_id: str, status: str) -> int:
    result = donations_collection().update_one(
        {"_id": _to_object_id(donation_id)}, {"$set": {"status": status}}
    )
    return result.modified_count


# Lists recent donations with optional status filter
def list_donations(
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    query: Dict[str, Any] = {}
    if status:
        query["status"] = status
    cursor = donations_collection().find(query).sort("created_at", -1).limit(limit)
    return [_serialize_id(doc) for doc in cursor]


# Aggregates donation counts by status
def summary_by_status() -> Dict[str, int]:
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    results = donations_collection().aggregate(pipeline)
    return {row["_id"]: row["count"] for row in results}


# Coerces string ids to ObjectId
def _to_object_id(value: str) -> ObjectId:
    return ObjectId(value)


# Converts ObjectId to string for CLI output
def _serialize_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# Checks if a string is a valid ObjectId
def _is_object_id(value: str) -> bool:
    return ObjectId.is_valid(value)


# Finds a record by case-insensitive exact name
def _find_one_by_name(collection: Collection, name: str) -> Optional[Dict[str, Any]]:
    pattern = f"^{re.escape(name.strip())}$"
    return collection.find_one({"name": {"$regex": pattern, "$options": "i"}})


# Resolves donor name or id to canonical id
def resolve_donor_id(value: str) -> str:
    if _is_object_id(value):
        return value
    match = _find_one_by_name(donors_collection(), value)
    if not match:
        raise ValueError(f"Donor not found: {value}")
    return str(match["_id"])


# Resolves recipient name or id to canonical id
def resolve_recipient_id(value: str) -> str:
    if _is_object_id(value):
        return value
    match = _find_one_by_name(recipients_collection(), value)
    if not match:
        raise ValueError(f"Recipient not found: {value}")
    return str(match["_id"])
