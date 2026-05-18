from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional

from .data_handling import (
    add_donation,
    list_donations,
    list_donors,
    list_recipients,
    register_donor,
    register_recipient,
    resolve_donor_id,
    resolve_recipient_id,
    summary_by_status,
    update_donation_status,
)
from .interface import STATUS_CHOICES
from .utils.helpers import format_key_values, format_table


class IntrackGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Intrack")
        self.minsize(980, 720)

        self._donor_options: Dict[str, str] = {}
        self._recipient_options: Dict[str, str] = {}
        self._donation_items: List[Dict[str, str]] = []

        self._build_ui()
        self._refresh_options()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        controls = ttk.Frame(container)
        controls.grid(row=0, column=0, sticky="nsew")
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        self._build_register_donor(controls)
        self._build_register_recipient(controls)
        self._build_add_donation(controls)
        self._build_list_donations(controls)
        self._build_update_status(controls)
        self._build_summary_controls(controls)

        output_frame = ttk.Labelframe(container, text="Console output", padding=8)
        output_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        container.rowconfigure(1, weight=1)

        self._output = ScrolledText(output_frame, height=12, wrap="word", state="disabled")
        self._output.grid(row=0, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

    def _build_register_donor(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Register donor", padding=8)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Type").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text="Contact").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="Address").grid(row=3, column=0, sticky="w")

        self.donor_name = ttk.Entry(frame)
        self.donor_type = ttk.Entry(frame)
        self.donor_contact = ttk.Entry(frame)
        self.donor_address = ttk.Entry(frame)
        self.donor_name.grid(row=0, column=1, sticky="ew")
        self.donor_type.grid(row=1, column=1, sticky="ew")
        self.donor_contact.grid(row=2, column=1, sticky="ew")
        self.donor_address.grid(row=3, column=1, sticky="ew")

        ttk.Button(frame, text="Register donor", command=self._on_register_donor).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

    def _build_register_recipient(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Register recipient", padding=8)
        frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Type").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text="Contact").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="Address").grid(row=3, column=0, sticky="w")

        self.recipient_name = ttk.Entry(frame)
        self.recipient_type = ttk.Entry(frame)
        self.recipient_contact = ttk.Entry(frame)
        self.recipient_address = ttk.Entry(frame)
        self.recipient_name.grid(row=0, column=1, sticky="ew")
        self.recipient_type.grid(row=1, column=1, sticky="ew")
        self.recipient_contact.grid(row=2, column=1, sticky="ew")
        self.recipient_address.grid(row=3, column=1, sticky="ew")

        ttk.Button(frame, text="Register recipient", command=self._on_register_recipient).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

    def _build_add_donation(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Add donation", padding=8)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
        for col in range(4):
            frame.columnconfigure(col, weight=1)

        ttk.Label(frame, text="Donor (dropdown)").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Donor (name/id)").grid(row=0, column=1, sticky="w")
        ttk.Label(frame, text="Recipient (dropdown)").grid(row=0, column=2, sticky="w")
        ttk.Label(frame, text="Recipient (name/id)").grid(row=0, column=3, sticky="w")

        self.donation_donor_combo = ttk.Combobox(frame, state="readonly")
        self.donation_donor_entry = ttk.Entry(frame)
        self.donation_recipient_combo = ttk.Combobox(frame, state="readonly")
        self.donation_recipient_entry = ttk.Entry(frame)
        self.donation_donor_combo.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self.donation_donor_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6))
        self.donation_recipient_combo.grid(row=1, column=2, sticky="ew", padx=(0, 6))
        self.donation_recipient_entry.grid(row=1, column=3, sticky="ew")

        ttk.Label(frame, text="Status").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.donation_status_combo = ttk.Combobox(
            frame, state="readonly", values=STATUS_CHOICES
        )
        self.donation_status_combo.set("available")
        self.donation_status_combo.grid(row=3, column=0, sticky="ew", padx=(0, 6))

        ttk.Label(frame, text="Item name").grid(row=2, column=1, sticky="w", pady=(6, 0))
        ttk.Label(frame, text="Quantity").grid(row=2, column=2, sticky="w", pady=(6, 0))
        ttk.Label(frame, text="Unit").grid(row=2, column=3, sticky="w", pady=(6, 0))
        self.item_name = ttk.Entry(frame)
        self.item_quantity = ttk.Entry(frame)
        self.item_unit = ttk.Entry(frame)
        self.item_name.grid(row=3, column=1, sticky="ew", padx=(0, 6))
        self.item_quantity.grid(row=3, column=2, sticky="ew", padx=(0, 6))
        self.item_unit.grid(row=3, column=3, sticky="ew")

        ttk.Label(frame, text="Category").grid(row=4, column=1, sticky="w", pady=(6, 0))
        ttk.Label(frame, text="Expiry (YYYY-MM-DD)").grid(
            row=4, column=2, sticky="w", pady=(6, 0)
        )
        self.item_category = ttk.Entry(frame)
        self.item_expiry = ttk.Entry(frame)
        self.item_category.grid(row=5, column=1, sticky="ew", padx=(0, 6))
        self.item_expiry.grid(row=5, column=2, sticky="ew", padx=(0, 6))

        ttk.Button(frame, text="Add item", command=self._on_add_item).grid(
            row=5, column=3, sticky="ew"
        )
        ttk.Button(frame, text="Clear items", command=self._on_clear_items).grid(
            row=6, column=3, sticky="ew", pady=(6, 0)
        )

        self.items_list = ttk.Treeview(
            frame, columns=("name", "qty", "unit", "cat", "exp"), show="headings", height=4
        )
        for col, label in [
            ("name", "Name"),
            ("qty", "Qty"),
            ("unit", "Unit"),
            ("cat", "Category"),
            ("exp", "Expiry"),
        ]:
            self.items_list.heading(col, text=label)
            self.items_list.column(col, width=120, anchor="w")
        self.items_list.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(6, 0))

        ttk.Button(frame, text="Add donation", command=self._on_add_donation).grid(
            row=7, column=0, columnspan=4, sticky="ew", pady=(8, 0)
        )

        ttk.Button(frame, text="Refresh donors/recipients", command=self._refresh_options).grid(
            row=8, column=0, columnspan=4, sticky="ew", pady=(6, 0)
        )

    def _build_list_donations(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="List donations", padding=8)
        frame.grid(row=2, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Status").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Limit").grid(row=1, column=0, sticky="w")
        self.list_status = ttk.Combobox(
            frame, state="readonly", values=[""] + STATUS_CHOICES
        )
        self.list_status.set("")
        self.list_limit = ttk.Entry(frame)
        self.list_limit.insert(0, "25")
        self.list_status.grid(row=0, column=1, sticky="ew")
        self.list_limit.grid(row=1, column=1, sticky="ew")

        ttk.Button(frame, text="List donations", command=self._on_list_donations).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

    def _build_update_status(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Update status", padding=8)
        frame.grid(row=2, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Donation id").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Status").grid(row=1, column=0, sticky="w")
        self.update_id = ttk.Entry(frame)
        self.update_status = ttk.Combobox(frame, state="readonly", values=STATUS_CHOICES)
        self.update_status.set("reserved")
        self.update_id.grid(row=0, column=1, sticky="ew")
        self.update_status.grid(row=1, column=1, sticky="ew")

        ttk.Button(frame, text="Update status", command=self._on_update_status).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

    def _build_summary_controls(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Summary", padding=8)
        frame.grid(row=3, column=0, columnspan=2, sticky="nsew")

        ttk.Button(frame, text="Show summary", command=self._on_summary).grid(
            row=0, column=0, sticky="ew"
        )

    def _append_output(self, text: str) -> None:
        self._output.configure(state="normal")
        self._output.insert("end", text + "\n")
        self._output.see("end")
        self._output.configure(state="disabled")

    def _refresh_options(self) -> None:
        donors = list_donors()
        recipients = list_recipients()

        self._donor_options = {self._format_option(d): d["_id"] for d in donors}
        self._recipient_options = {
            self._format_option(r): r["_id"] for r in recipients
        }

        self.donation_donor_combo["values"] = list(self._donor_options.keys())
        self.donation_recipient_combo["values"] = list(self._recipient_options.keys())

        if self.donation_donor_combo.get() not in self._donor_options:
            self.donation_donor_combo.set("")
        if self.donation_recipient_combo.get() not in self._recipient_options:
            self.donation_recipient_combo.set("")

        self._append_output(
            format_key_values(
                {
                    "donors_loaded": str(len(donors)),
                    "recipients_loaded": str(len(recipients)),
                }
            )
        )

    def _format_option(self, doc: Dict[str, str]) -> str:
        name = doc.get("name", "")
        short_id = doc.get("_id", "")
        return f"{name} ({short_id})"

    def _pick_value(
        self, combo: ttk.Combobox, entry: ttk.Entry, mapping: Dict[str, str]
    ) -> Optional[str]:
        combo_value = combo.get().strip()
        if combo_value and combo_value in mapping:
            return mapping[combo_value]
        manual_value = entry.get().strip()
        return manual_value or None

    def _on_register_donor(self) -> None:
        try:
            donor_id = register_donor(
                self.donor_name.get(),
                self.donor_type.get(),
                self.donor_contact.get(),
                self.donor_address.get(),
            )
            self._append_output(format_key_values({"donor_id": donor_id}))
            self._refresh_options()
        except Exception as exc:
            self._append_output(str(exc))

    def _on_register_recipient(self) -> None:
        try:
            recipient_id = register_recipient(
                self.recipient_name.get(),
                self.recipient_type.get(),
                self.recipient_contact.get(),
                self.recipient_address.get(),
            )
            self._append_output(format_key_values({"recipient_id": recipient_id}))
            self._refresh_options()
        except Exception as exc:
            self._append_output(str(exc))

    def _on_add_item(self) -> None:
        name = self.item_name.get().strip()
        quantity = self.item_quantity.get().strip()
        if not name or not quantity:
            self._append_output("Item name and quantity are required.")
            return
        try:
            float(quantity)
        except ValueError:
            self._append_output("Quantity must be a number.")
            return

        item = {
            "name": name,
            "quantity": quantity,
            "unit": self.item_unit.get().strip() or "units",
            "category": self.item_category.get().strip() or None,
            "expiry_date": self.item_expiry.get().strip() or None,
        }
        self._donation_items.append(item)
        self.items_list.insert(
            "end",
            values=(
                item["name"],
                item["quantity"],
                item["unit"],
                item.get("category") or "",
                item.get("expiry_date") or "",
            ),
        )
        self.item_name.delete(0, "end")
        self.item_quantity.delete(0, "end")
        self.item_unit.delete(0, "end")
        self.item_category.delete(0, "end")
        self.item_expiry.delete(0, "end")

    def _on_clear_items(self) -> None:
        self._donation_items.clear()
        for row in self.items_list.get_children():
            self.items_list.delete(row)

    def _on_add_donation(self) -> None:
        donor_value = self._pick_value(
            self.donation_donor_combo, self.donation_donor_entry, self._donor_options
        )
        if not donor_value:
            self._append_output("Select a donor or enter a donor name/id.")
            return
        if not self._donation_items:
            self._append_output("Add at least one item before submitting.")
            return
        recipient_value = self._pick_value(
            self.donation_recipient_combo,
            self.donation_recipient_entry,
            self._recipient_options,
        )
        try:
            donor_id = resolve_donor_id(donor_value)
            recipient_id = resolve_recipient_id(recipient_value) if recipient_value else None
            donation_id = add_donation(
                donor_id,
                list(self._donation_items),
                recipient_id=recipient_id,
                status=self.donation_status_combo.get(),
            )
            self._append_output(format_key_values({"donation_id": donation_id}))
            self._on_clear_items()
        except Exception as exc:
            self._append_output(str(exc))

    def _on_list_donations(self) -> None:
        try:
            limit = int(self.list_limit.get() or "25")
            status = self.list_status.get().strip() or None
            rows = list_donations(status=status, limit=limit)
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
            self._append_output(format_table(printable, ["_id", "donor_id", "status", "created_at", "items"]))
        except Exception as exc:
            self._append_output(str(exc))

    def _on_update_status(self) -> None:
        donation_id = self.update_id.get().strip()
        if not donation_id:
            self._append_output("Donation id is required.")
            return
        try:
            modified = update_donation_status(donation_id, self.update_status.get())
            self._append_output(format_key_values({"updated": str(modified)}))
        except Exception as exc:
            self._append_output(str(exc))

    def _on_summary(self) -> None:
        try:
            summary = summary_by_status()
            self._append_output(
                format_table(
                    [{"status": k, "count": v} for k, v in summary.items()],
                    ["status", "count"],
                )
            )
        except Exception as exc:
            self._append_output(str(exc))


def run_gui() -> int:
    app = IntrackGUI()
    app.mainloop()
    return 0

