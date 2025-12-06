import csv
from pathlib import Path

from .config import HEADERS
from .scrapers.wikipedia_scraper import WikipediaScraper
from .run import build_wikipedia_map


CHUNK_SIZE = 10


def enrich_kdrama_list(
    input_csv: str | Path | None = None,
    wikipedia_list_path: str | Path | None = None,
    output_csv: str | Path | None = None,
) -> None:
    """
    Read an existing kdrama_list.csv, enrich each row with Wikipedia data (if available),
    and write out a new CSV with additional fields.
    """
    base_dir = Path(__file__).parent

    if input_csv is None:
        input_csv = base_dir / "data" / "kdrama_list.csv"
    else:
        input_csv = Path(input_csv)

    if wikipedia_list_path is None:
        wikipedia_list_path = base_dir / "data" / "wikipedia_list.json"
    else:
        wikipedia_list_path = Path(wikipedia_list_path)

    if output_csv is None:
        # Write to a new file so we don't overwrite the original IMDb-only CSV
        output_csv = base_dir / "data" / "kdrama_list_with_wiki.csv"
    else:
        output_csv = Path(output_csv)

    print(f"Loading Wikipedia mapping from {wikipedia_list_path}")
    title_to_url = build_wikipedia_map(wikipedia_list_path)

    print(f"Loading input CSV from {input_csv}")
    with open(input_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        existing_fieldnames = reader.fieldnames or []

    if not rows:
        print("No rows found in input CSV. Nothing to enrich.")
        return

    total = len(rows)
    print(f"Loaded {total} dramas from {input_csv}")

    extra_fields = ["network_provider", "screenwriter", "director", "plot", "source"]
    fieldnames = existing_fieldnames + [f for f in extra_fields if f not in existing_fieldnames]

    # Process in chunks so progress can be monitored
    for start in range(0, total, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE, total)
        chunk = rows[start:end]
        chunk_index = start // CHUNK_SIZE + 1

        attempts = 0
        successes = 0

        for row in chunk:
            title = (row.get("title") or "").strip()
            if not title:
                continue

            wiki_url = title_to_url.get(title)
            if not wiki_url:
                # No Wikipedia entry mapped for this title
                continue

            attempts += 1

            wscraper = WikipediaScraper(wiki_url, HEADERS)
            info_list = wscraper.get_info_list()

            # If we couldn't fetch or parse the page, skip this drama
            if not info_list:
                continue

            info = info_list[0]
            row["network_provider"] = info.get("network", "")
            row["screenwriter"] = ", ".join(info.get("screenwriter", []))
            row["director"] = ", ".join(info.get("director", []))
            row["plot"] = info.get("plot", "")
            row["source"] = wiki_url
            successes += 1

        print(
            f"Chunk {chunk_index}: rows {start + 1}-{end} | "
            f"attempted {attempts} Wikipedia lookups | successes {successes}"
        )

    # Write out the enriched CSV (original rows are preserved; extra fields added when present)
    print(f"Writing enriched CSV to {output_csv}")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("Done enriching kdrama list with Wikipedia data.")


if __name__ == "__main__":
    enrich_kdrama_list()


