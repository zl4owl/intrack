from typing import Dict, Iterable, List


# Builds a fixed-width table for CLI output
def format_table(rows: Iterable[Dict[str, str]], headers: List[str]) -> str:
    rows_list = list(rows)
    if not rows_list:
        return "(no results)"
    widths = {h: len(h) for h in headers}
    for row in rows_list:
        for header in headers:
            widths[header] = max(widths[header], len(str(row.get(header, ""))))
    line_parts = ["-" * widths[h] for h in headers]
    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    separator = "-+-".join(line_parts)
    body = "\n".join(
        " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        for row in rows_list
    )
    return "\n".join([header_line, separator, body])


# Formats key/value pairs in aligned columns
def format_key_values(values: Dict[str, str]) -> str:
    width = max((len(k) for k in values), default=0)
    return "\n".join(f"{k.rjust(width)} : {v}" for k, v in values.items())
