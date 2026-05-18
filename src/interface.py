from __future__ import annotations

import argparse
import shlex
from typing import Dict, List, Optional
from dataclasses import dataclass

from .data_handling import (
    add_donation,
    list_donations,
    register_donor,
    register_recipient,
    resolve_donor_id,
    resolve_recipient_id,
    summary_by_status,
    update_donation_status,
)
from .utils.helpers import format_key_values, format_table

STATUS_CHOICES = ["available", "reserved", "picked_up", "distributed", "expired"]
DEFAULT_ORG_TYPE = "organization"

COMMAND_ALIASES = {
    "reg-donor": "register-donor",
    "reg-rec": "register-recipient",
    "add": "add-donation",
    "list": "list-donations",
    "status": "update-status",
    "sum": "summary",
    "org": "use-org",
}

@dataclass
class ConsoleState:
    current_donor_id: Optional[str] = None


def _parse_item_arg(value: str) -> Dict[str, str]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            "Item must be 'name,quantity[,unit,category,expiry_date]'"
        )
    name, quantity = parts[0], parts[1]
    unit = parts[2] if len(parts) > 2 and parts[2] else "units"
    category = parts[3] if len(parts) > 3 and parts[3] else None
    expiry_date = parts[4] if len(parts) > 4 and parts[4] else None
    return {
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "category": category,
        "expiry_date": expiry_date,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track food donations for supermarkets and organizations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    donor = subparsers.add_parser(
        "register-donor",
        aliases=["reg-donor"],
        help="Register a donor.",
    )
    donor.add_argument("name")
    donor.add_argument("type")
    donor.add_argument("contact")
    donor.add_argument("address", nargs="?")

    recipient = subparsers.add_parser(
        "register-recipient",
        aliases=["reg-rec"],
        help="Register a recipient organization.",
    )
    recipient.add_argument("name")
    recipient.add_argument("type")
    recipient.add_argument("contact")
    recipient.add_argument("address", nargs="?")

    donation = subparsers.add_parser(
        "add-donation",
        aliases=["add"],
        help="Add a donation batch.",
    )
    donation.add_argument("donor_id", nargs="?")
    donation.add_argument(
        "--item",
        action="append",
        required=True,
        type=_parse_item_arg,
        help="Repeatable item: name,quantity[,unit,category,expiry_date]",
    )
    donation.add_argument("--recipient-id")
    donation.add_argument("--status", choices=STATUS_CHOICES, default="available")

    list_cmd = subparsers.add_parser(
        "list-donations",
        aliases=["list"],
        help="List donations.",
    )
    list_cmd.add_argument("--status", choices=STATUS_CHOICES)
    list_cmd.add_argument("--limit", type=int, default=25)

    update_cmd = subparsers.add_parser(
        "update-status",
        aliases=["status"],
        help="Update donation status.",
    )
    update_cmd.add_argument("donation_id")
    update_cmd.add_argument("status", choices=STATUS_CHOICES)

    use_org = subparsers.add_parser(
        "use-org",
        aliases=["org"],
        help="Set current donor organization (console).",
    )
    use_org.add_argument("donor", help="Donor name or id")

    subparsers.add_parser("summary", aliases=["sum"], help="Show donation counts by status.")

    return parser


def _execute_command(parsed: argparse.Namespace, state: Optional[ConsoleState] = None) -> int:
    if parsed.command == "register-donor":
        donor_id = register_donor(parsed.name, parsed.type, parsed.contact, parsed.address)
        print(format_key_values({"donor_id": donor_id}))
        return 0

    if parsed.command == "register-recipient":
        recipient_id = register_recipient(
            parsed.name, parsed.type, parsed.contact, parsed.address
        )
        print(format_key_values({"recipient_id": recipient_id}))
        return 0

    if parsed.command == "use-org":
        resolved = resolve_donor_id(parsed.donor)
        if state is not None:
            state.current_donor_id = resolved
        print(format_key_values({"current_donor_id": resolved}))
        return 0

    if parsed.command == "add-donation":
        donor_value = parsed.donor_id or (state.current_donor_id if state else None)
        if not donor_value:
            raise ValueError("Donor id or name is required. Use 'use-org' in console.")
        donor_id = resolve_donor_id(donor_value)
        recipient_id = (
            resolve_recipient_id(parsed.recipient_id)
            if parsed.recipient_id
            else None
        )
        donation_id = add_donation(
            donor_id,
            parsed.item,
            recipient_id=recipient_id,
            status=parsed.status,
        )
        print(format_key_values({"donation_id": donation_id}))
        return 0

    if parsed.command == "list-donations":
        rows = list_donations(status=parsed.status, limit=parsed.limit)
        printable = [
            {
                "_id": row.get("_id"),
                "donor_id": row.get("donor_id"),
                "status": row.get("status"),
                "created_at": row.get("created_at"),
                "items": len(row.get("items", [])),
            }
            for row in rows
        ]
        print(format_table(printable, ["_id", "donor_id", "status", "created_at", "items"]))
        return 0

    if parsed.command == "update-status":
        modified = update_donation_status(parsed.donation_id, parsed.status)
        if modified:
            print(format_key_values({"updated": "1"}))
            return 0
        print(format_key_values({"updated": "0"}))
        return 1

    if parsed.command == "summary":
        summary = summary_by_status()
        print(format_table(
            [{"status": k, "count": v} for k, v in summary.items()],
            ["status", "count"],
        ))
        return 0

    raise ValueError("Unknown command")


def run_cli(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args=args)
    return _execute_command(parsed)


def run_console() -> int:
    parser = build_parser()
    state = ConsoleState()
    print("Intrack interactive console. Type 'help' or 'exit'.")
    while True:
        try:
            line = input("intrack> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not line:
            continue

        if line in {"exit", "quit"}:
            return 0

        if line.startswith("help"):
            parts = shlex.split(line)
            if len(parts) == 1:
                parser.print_help()
                continue
            try:
                parser.parse_args([parts[1], "--help"])
            except SystemExit:
                pass
            continue

        try:
            raw_tokens = shlex.split(line)
            parsed = parser.parse_args(_normalize_console_tokens(raw_tokens))
        except SystemExit:
            continue

        try:
            _execute_command(parsed, state=state)
        except ValueError as exc:
            print(str(exc))



def _normalize_console_tokens(tokens: List[str]) -> List[str]:
    if not tokens:
        return tokens
    command = COMMAND_ALIASES.get(tokens[0], tokens[0])
    tokens = [command] + tokens[1:]

    if command in {"register-donor", "register-recipient"}:
        # If user entered just name + contact, insert default type
        if len(tokens) == 3:
            tokens.insert(2, DEFAULT_ORG_TYPE)
    return tokens
