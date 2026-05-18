# AS 91896 & AS 91897 - Computer Program

## Description

### Summery

A program designed to track food donations and manage their redistribution. This program has a focus on intuitiveness, elegance, and efficiency.  

### Dependancies 

- Pandas
- SciPy
- MatPlotLib

## Command Line Usage

This CLI tracks food donations for supermarkets, organizations, and institutions using a central MongoDB database.

### Environment

- `MONGODB_URI` (optional): overrides the default URI in code.
- `MONGODB_DB` (optional): overrides the database name (default: `food_donations`).

### Examples

Register a donor and recipient:

```bash
python program.py register-donor "FreshMart" supermarket "donations@freshmart.co" "12 Main St"
python program.py register-recipient "City Foodbank" foodbank "intake@cityfb.org" "88 Relief Rd"
```

Add a donation batch with multiple items:

```bash
python program.py add-donation DONOR_ID \
  --item "apples,25,kg,produce,2026-05-25" \
  --item "canned beans,80,units,pantry,2027-01-01"
```

List and update:

```bash
python program.py list-donations --status available --limit 10
python program.py update-status DONATION_ID reserved
python program.py summary
```

## User Documentation

### What This Tool Does

Tracks food donations from donors (supermarkets, farms, restaurants) to recipients (foodbanks, shelters, schools) in a central MongoDB database.

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

1. CLI input → parsed in `src/interface.py` and validated for structure.
2. Normalization → item names are lowercased/trimmed; dates are validated as `YYYY-MM-DD` in `src/data_handling.py`.
3. Document creation → donation docs are built with normalized items and UTC timestamps.
4. Database write → MongoDB inserts are performed on the central DB collections.
5. Read operations → queries return MongoDB documents, `_id` fields are converted to strings for CLI output.
6. Status updates → donation `_id` is converted back to `ObjectId` before updating.

### Commands

Register donor:

```bash
python program.py register-donor "NAME" "TYPE" "CONTACT" "ADDRESS"
```

Register recipient:

```bash
python program.py register-recipient "NAME" "TYPE" "CONTACT" "ADDRESS"
```

Add donation (repeat `--item`):

```bash
python program.py add-donation DONOR_ID \
  --item "NAME,QUANTITY[,UNIT,CATEGORY,EXPIRY_DATE]" \
  --item "NAME,QUANTITY[,UNIT,CATEGORY,EXPIRY_DATE]"
```

List donations:

```bash
python program.py list-donations --status available --limit 10
```

Update status:

```bash
python program.py update-status DONATION_ID reserved
```

Summary:

```bash
python program.py summary
```

### Environment Variables

- `MONGODB_URI`: override the default MongoDB URI.
- `MONGODB_DB`: override the database name (default `food_donations`).
