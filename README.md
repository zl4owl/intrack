# Intrack

## Description

### Summery

A cli based program designed to track food donations and manage their redistribution. This program has a focus on intuitiveness, elegance, and efficiency.  

### Dependancies 

- Pandas
- SciPy
- MatPlotLib

### Environment

- `MONGODB_URI` (optional): overrides the default URI in code.
- `MONGODB_DB` (optional): overrides the database name (default: `food_donations`).

### Examples

Start the Tkinter GUI (default):

```bash
python intrack.py
```

Use the CLI instead of the GUI:

```bash
python intrack.py --no-gui list-donations --status available --limit 10
```

Start the interactive console (CLI mode):

```bash
python intrack.py --no-gui
```

Register a donor and recipient:

```bash
python intrack.py register-donor "Freshchoice" supermarket "office@freshchoicetitirangi.co.nz" "429 Titirangi Road, Titirangi, Auckland 0604"
python intrack.py register-recipient "Auckland City Mission" foodbank "info@aucklandcitymission.org.nz" "127 Symonds Street"
```

Add a donation batch with multiple items:

```bash
python intrack.py add-donation DONOR_ID \
  --item "apples,25,kg,produce,2026-05-25" \
  --item "canned beans,80,units,pantry,2027-01-01"
```

List and update:

```bash
python intrack.py list-donations --status available --limit 10
python intrack.py update-status DONATION_ID reserved
python intrack.py summary
```

Seed demo data (four donors, four recipients, and random donations):

```bash
python3 seed_data.py
```

Delete only the seeded demo data:

```bash
python3 seed_data.py --delete-seeded
```

Clear all donors, recipients, and donations:

```bash
python3 seed_data.py --clear-db
```

## User Documentation

### What This Tool Does

Tracks food donations from donors (supermarkets, farms, restaurants) to recipients (foodbanks, shelters, schools) in a database.

### Data

- Donor: `name`, `type`, `contact`, `address`, `created_at`
- Recipient: `name`, `type`, `contact`, `address`, `created_at`
- Donation:
  - `donor_id` (string MongoDB ObjectId)
  - `recipient_id` (optional string ObjectId)
  - `items[]` (each item has `name`, `quantity`, `unit`, `category`, `expiry_date`)
  - `status` (`available`, `reserved`, `picked_up`, `distributed`, `expired`)
  - `created_at` (UTC timestamp)

### Management & Transfer of Data

1. CLI input → parsed in `src/interface.py`.
2. Normalization → item names are lowercased/trimmed; dates are validated as `YYYY-MM-DD` in `src/data_handling.py`.
3. Document creation → donation docs are built with normalized items and UTC timestamps.
4. Database write → MongoDB inserts are performed on the central DB collections.
5. Read operations → queries return MongoDB documents, `_id` fields are converted to strings for CLI output.
6. Status updates → donation `_id` is converted back to `ObjectId` before updating.

### Commands

Short aliases (interactive or CLI):

- `reg-donor` → `register-donor`
- `reg-rec` → `register-recipient`
- `add` → `add-donation`
- `list` → `list-donations`
- `status` → `update-status`
- `sum` → `summary`

Interactive quick entry (type defaults to `organization` if omitted):

```bash
python intrack.py --no-gui
intrack> org "FreshMart"
intrack> add --item "bread,20,loaves,bakery,2026-05-21"
```

Register donor:

```bash
python intrack.py register-donor "NAME" "TYPE" "CONTACT" "ADDRESS"
```

Register recipient:

```bash
python intrack.py register-recipient "NAME" "TYPE" "CONTACT" "ADDRESS"
```

Add donation (repeat `--item`):

```bash
python intrack.py add-donation DONOR_NAME_OR_ID \
  --item "NAME,QUANTITY[,UNIT,CATEGORY,EXPIRY_DATE]" \
  --recipient-id "RECIPIENT_NAME_OR_ID"
```

List donations:

```bash
python intrack.py list-donations --status available --limit 10
```

Update status:

```bash
python intrack.py update-status DONATION_ID reserved
```

Summary:

```bash
python intrack.py summary
``` 