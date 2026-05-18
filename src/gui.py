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
        self.minsize(1100, 760)

        self._donor_options: Dict[str, str] = {}
        self._donor_by_id: Dict[str, str] = {}
        self._recipient_options: Dict[str, str] = {}
        self._donation_items: List[Dict[str, str]] = []
        self.current_org_id: Optional[str] = None

        self._build_ui()
        self._refresh_options()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(3, weight=1)

        ttk.Label(header, text="Current organization").grid(row=0, column=0, sticky="w")
        self.current_org_combo = ttk.Combobox(header, state="readonly", width=38)
        self.current_org_entry = ttk.Entry(header, width=30)
        self.current_org_combo.grid(row=0, column=1, sticky="ew", padx=(8, 6))
        self.current_org_entry.grid(row=0, column=2, sticky="ew")
        ttk.Button(header, text="Set", command=self._set_current_org).grid(
            row=0, column=3, sticky="w", padx=(8, 0)
        )
        self.current_org_label = ttk.Label(header, text="Not set")
        self.current_org_label.grid(row=0, column=4, sticky="w", padx=(12, 0))
        ttk.Button(header, text="Refresh", command=self._refresh_options).grid(
            row=0, column=5, sticky="e", padx=(12, 0)
        )

        body = ttk.Frame(container)
        body.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(body)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self._build_donations_tab()
        self._build_orgs_tab()
        self._build_reports_tab()

        output_frame = ttk.Labelframe(container, text="Console output", padding=8)
        output_frame.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        container.rowconfigure(2, weight=1)

        self._output = ScrolledText(output_frame, height=10, wrap="word", state="disabled")
        self._output.grid(row=0, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

    def _build_donations_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        tab.columnconfigure(0, weight=2)
        tab.columnconfigure(1, weight=3)
        tab.rowconfigure(0, weight=1)
        self.notebook.add(tab, text="Donations")

        form = ttk.Labelframe(tab, text="Quick donation", padding=8)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        for col in range(3):
            form.columnconfigure(col, weight=1)

        ttk.Label(form, text="Donor (dropdown)").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Donor (name/id)").grid(row=0, column=1, sticky="w")
        self.donation_donor_combo = ttk.Combobox(form, state="readonly")
        self.donation_donor_entry = ttk.Entry(form)
        self.donation_donor_combo.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self.donation_donor_entry.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ttk.Label(form, text="Recipient (dropdown)").grid(row=0, column=2, sticky="w")
        self.donation_recipient_combo = ttk.Combobox(form, state="readonly")
        self.donation_recipient_combo.grid(row=1, column=2, sticky="ew")
        ttk.Label(form, text="Recipient (name/id)").grid(row=2, column=2, sticky="w", pady=(6, 0))
        self.donation_recipient_entry = ttk.Entry(form)
        self.donation_recipient_entry.grid(row=3, column=2, sticky="ew")

        ttk.Label(form, text="Status").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.donation_status_combo = ttk.Combobox(
            form, state="readonly", values=STATUS_CHOICES
        )
        self.donation_status_combo.set("available")
        self.donation_status_combo.grid(row=3, column=0, sticky="ew", padx=(0, 6))

        ttk.Label(form, text="Item name").grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Quantity").grid(row=4, column=1, sticky="w", pady=(8, 0))
        ttk.Label(form, text="Unit").grid(row=4, column=2, sticky="w", pady=(8, 0))
        self.item_name = ttk.Entry(form)
        self.item_quantity = ttk.Entry(form)
        self.item_unit = ttk.Entry(form)
        self.item_name.grid(row=5, column=0, sticky="ew", padx=(0, 6))
        self.item_quantity.grid(row=5, column=1, sticky="ew", padx=(0, 6))
        self.item_unit.grid(row=5, column=2, sticky="ew")

        ttk.Label(form, text="Category").grid(row=6, column=0, sticky="w", pady=(6, 0))
        ttk.Label(form, text="Expiry (YYYY-MM-DD)").grid(
            row=6, column=1, sticky="w", pady=(6, 0)
        )
        self.item_category = ttk.Entry(form)
        self.item_expiry = ttk.Entry(form)
        self.item_category.grid(row=7, column=0, sticky="ew", padx=(0, 6))
        self.item_expiry.grid(row=7, column=1, sticky="ew", padx=(0, 6))

        ttk.Button(form, text="Add item", command=self._on_add_item).grid(
            row=7, column=2, sticky="ew"
        )
        ttk.Button(form, text="Clear items", command=self._on_clear_items).grid(
            row=8, column=2, sticky="ew", pady=(6, 0)
        )

        self.items_list = ttk.Treeview(
            form, columns=("name", "qty", "unit", "cat", "exp"), show="headings", height=5
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
        self.items_list.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        ttk.Button(form, text="Submit donation", command=self._on_add_donation).grid(
            row=9, column=0, columnspan=3, sticky="ew", pady=(10, 0)
        )

        list_frame = ttk.Labelframe(tab, text="Recent donations", padding=8)
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        controls = ttk.Frame(list_frame)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(4, weight=1)

        ttk.Label(controls, text="Status").grid(row=0, column=0, sticky="w")
        self.list_status = ttk.Combobox(
            controls, state="readonly", values=[""] + STATUS_CHOICES, width=14
        )
        self.list_status.set("")
        self.list_status.grid(row=0, column=1, sticky="w", padx=(6, 12))
        ttk.Label(controls, text="Limit").grid(row=0, column=2, sticky="w")
        self.list_limit = ttk.Entry(controls, width=8)
        self.list_limit.insert(0, "25")
        self.list_limit.grid(row=0, column=3, sticky="w", padx=(6, 12))
        ttk.Button(controls, text="Refresh", command=self._on_list_donations).grid(
            row=0, column=4, sticky="e"
        )

        self.donations_list = ttk.Treeview(
            list_frame,
            columns=("_id", "donor_id", "status", "created_at", "items"),
            show="headings",
            height=12,
        )
        for col, label, width in [
            ("_id", "ID", 220),
            ("donor_id", "Donor", 220),
            ("status", "Status", 100),
            ("created_at", "Created", 150),
            ("items", "Items", 60),
        ]:
            self.donations_list.heading(col, text=label)
            self.donations_list.column(col, width=width, anchor="w")
        self.donations_list.grid(row=1, column=0, sticky="nsew")

        update_frame = ttk.Labelframe(tab, text="Update status", padding=8)
        update_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        update_frame.columnconfigure(1, weight=1)

        ttk.Label(update_frame, text="Donation id").grid(row=0, column=0, sticky="w")
        self.update_id = ttk.Entry(update_frame)
        self.update_id.grid(row=0, column=1, sticky="ew", padx=(6, 12))
        ttk.Label(update_frame, text="Status").grid(row=0, column=2, sticky="w")
        self.update_status = ttk.Combobox(
            update_frame, state="readonly", values=STATUS_CHOICES, width=16
        )
        self.update_status.set("reserved")
        self.update_status.grid(row=0, column=3, sticky="w", padx=(6, 12))
        ttk.Button(update_frame, text="Update", command=self._on_update_status).grid(
            row=0, column=4, sticky="e"
        )

    def _build_orgs_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        self.notebook.add(tab, text="Organizations")

        self._build_register_donor(tab, 0)
        self._build_register_recipient(tab, 1)

    def _build_reports_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        tab.columnconfigure(0, weight=1)
        self.notebook.add(tab, text="Reports")

        frame = ttk.Labelframe(tab, text="Summary", padding=8)
        frame.grid(row=0, column=0, sticky="nw")
        ttk.Button(frame, text="Show summary", command=self._on_summary).grid(
            row=0, column=0, sticky="ew"
        )

    def _build_register_donor(self, parent: ttk.Frame, column: int) -> None:
        frame = ttk.Labelframe(parent, text="Register donor", padding=8)
        frame.grid(row=0, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0))
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

    def _build_register_recipient(self, parent: ttk.Frame, column: int) -> None:
        frame = ttk.Labelframe(parent, text="Register recipient", padding=8)
        frame.grid(row=0, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0))
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

        ttk.Button(
            frame, text="Register recipient", command=self._on_register_recipient
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))

    def _append_output(self, text: str) -> None:
        self._output.configure(state="normal")
        self._output.insert("end", text + "\n")
        self._output.see("end")
        self._output.configure(state="disabled")

    def _refresh_options(self) -> None:
        donors = list_donors()
        recipients = list_recipients()

        self._donor_options = {self._format_option(d): d["_id"] for d in donors}
        self._donor_by_id = {d["_id"]: self._format_option(d) for d in donors}
        self._recipient_options = {
            self._format_option(r): r["_id"] for r in recipients
        }

        donor_values = list(self._donor_options.keys())
        recipient_values = list(self._recipient_options.keys())

        self.donation_donor_combo["values"] = donor_values
        self.current_org_combo["values"] = donor_values
        self.donation_recipient_combo["values"] = recipient_values

        if self.donation_donor_combo.get() not in self._donor_options:
            self.donation_donor_combo.set("")
        if self.donation_recipient_combo.get() not in self._recipient_options:
            self.donation_recipient_combo.set("")
        if self.current_org_combo.get() not in self._donor_options:
            self.current_org_combo.set("")

        self._update_current_org_label()
        self._append_output(
            format_key_values(
                {
                    "donors_loaded": str(len(donors)),
                    "recipients_loaded": str(len(recipients)),
                }
            )
        )

    def _update_current_org_label(self) -> None:
        if not self.current_org_id:
            self.current_org_label.configure(text="Not set")
            return
        label = self._donor_by_id.get(self.current_org_id, self.current_org_id)
        self.current_org_label.configure(text=label)

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

    def _set_current_org(self) -> None:
        donor_value = self._pick_value(
            self.current_org_combo, self.current_org_entry, self._donor_options
        )
        if not donor_value:
            self._append_output("Select a donor or enter a donor name/id.")
            return
        try:
            self.current_org_id = resolve_donor_id(donor_value)
            self._update_current_org_label()
            self._append_output(format_key_values({"current_org": self.current_org_id}))
        except Exception as exc:
            self._append_output(str(exc))

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

    def _resolve_donor(self) -> Optional[str]:
        donor_value = self._pick_value(
            self.donation_donor_combo, self.donation_donor_entry, self._donor_options
        )
        if donor_value:
            return resolve_donor_id(donor_value)
        if self.current_org_id:
            return self.current_org_id
        return None

    def _on_add_donation(self) -> None:
        if not self._donation_items:
            self._append_output("Add at least one item before submitting.")
            return
        try:
            donor_id = self._resolve_donor()
            if not donor_id:
                self._append_output("Set a current org or select a donor.")
                return
        except Exception as exc:
            self._append_output(str(exc))
            return

        recipient_value = self._pick_value(
            self.donation_recipient_combo,
            self.donation_recipient_entry,
            self._recipient_options,
        )
        try:
            recipient_id = resolve_recipient_id(recipient_value) if recipient_value else None
            donation_id = add_donation(
                donor_id,
                list(self._donation_items),
                recipient_id=recipient_id,
                status=self.donation_status_combo.get(),
            )
            self._append_output(format_key_values({"donation_id": donation_id}))
            self._on_clear_items()
            self._on_list_donations()
        except Exception as exc:
            self._append_output(str(exc))

    def _on_list_donations(self) -> None:
        try:
            limit = int(self.list_limit.get() or "25")
            status = self.list_status.get().strip() or None
            rows = list_donations(status=status, limit=limit)
            self._render_donations(rows)
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
            self._append_output(
                format_table(printable, ["_id", "donor_id", "status", "created_at", "items"])
            )
        except Exception as exc:
            self._append_output(str(exc))

    def _render_donations(self, rows: List[Dict[str, str]]) -> None:
        for row in self.donations_list.get_children():
            self.donations_list.delete(row)
        for row in rows:
            self.donations_list.insert(
                "end",
                values=(
                    row.get("_id"),
                    row.get("donor_id"),
                    row.get("status"),
                    row.get("created_at"),
                    len(row.get("items", [])),
                ),
            )

    def _on_update_status(self) -> None:
        donation_id = self.update_id.get().strip()
        if not donation_id:
            self._append_output("Donation id is required.")
            return
        try:
            modified = update_donation_status(donation_id, self.update_status.get())
            self._append_output(format_key_values({"updated": str(modified)}))
            self._on_list_donations()
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

