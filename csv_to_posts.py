#!/usr/bin/env python3
import argparse
import csv
import re
from datetime import date
from pathlib import Path


LIST_FIELDS = {"category", "tags"}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def split_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def add_scalar(lines, key, value):
    if value is not None and str(value).strip():
        lines.append(f"{key}: {str(value).strip()}")


def add_list(lines, key, value):
    items = split_list(value)
    if items:
        lines.append(f"{key}:")
        for item in items:
            lines.append(f"  - {item}")


def build_post(row, blank_cover=False):
    name = row.get("name") or row.get("title")
    if not name:
        raise ValueError("Row is missing required field: name")

    lines = ["---"]

    add_scalar(lines, "name", name)
    add_list(lines, "category", row.get("category"))
    add_scalar(lines, "author", row.get("author"))
    add_scalar(lines, "source", row.get("source"))
    add_scalar(lines, "source-url", row.get("source-url") or row.get("source_url"))
    add_scalar(lines, "genre", row.get("genre"))
    add_scalar(lines, "summary", row.get("summary"))
    add_scalar(lines, "cost", row.get("cost"))
    add_scalar(lines, "license", row.get("license"))

    cover = row.get("cover-image") or row.get("cover_image")
    if cover:
        add_scalar(lines, "cover-image", cover)
    elif blank_cover:
        lines.append("cover-image:")

    add_list(lines, "tags", row.get("tags"))

    lines.append("---")

    body = row.get("body") or row.get("markdown") or row.get("description") or ""
    if body.strip():
        return "\n".join(lines) + "\n\n" + body.strip() + "\n"

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Convert a CSV into Gorlab markdown posts."
    )
    parser.add_argument("csv_file")
    parser.add_argument("-o", "--output", default="posts")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--blank-cover", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get("name") or row.get("title")
            if not name:
                print("Skipping row with no name/title")
                continue

            filename = f"{args.date}-{slugify(name)}.md"
            path = output_dir / filename

            path.write_text(build_post(row, args.blank_cover), encoding="utf-8")
            print(f"Wrote {path}")


if __name__ == "__main__":
    main()
