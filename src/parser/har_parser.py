import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import sys


def find_event_names(obj, found_events):
    """
    Recursively search for event 'name' fields in any dict/list structure.
    Only adds names where the parent dict looks like an event node.
    """
    if isinstance(obj, dict):
        # Heuristic: looks like an event node if it has 'name' and 'eventUrl' or '__typename' == 'Event'
        if "name" in obj and ("eventUrl" in obj or obj.get("__typename") == "Event"):
            found_events.append(obj["name"])
        # Continue searching all values
        for v in obj.values():
            find_event_names(v, found_events)
    elif isinstance(obj, list):
        for item in obj:
            find_event_names(item, found_events)


def central_time_from_timestamp(ts: int) -> str:
    """Convert epoch seconds (UTC) to America/Chicago local date-time string.

    Output example: '2025-10-04 9:00 PM CDT'
    - Uses America/Chicago and includes DST-aware timezone abbreviation.
    - Returns empty string on failure.
    """
    try:
        raw = int(ts)
        # Normalize milliseconds to seconds if needed
        if raw > 10**12:
            raw //= 1000
        dt_utc = datetime.fromtimestamp(raw, tz=timezone.utc)
        # Try to use America/Chicago; fallback to UTC if tz database not available
        try:
            tz_central = ZoneInfo("America/Chicago")
        except Exception:
            tz_central = None
        dt_local = dt_utc.astimezone(tz_central) if tz_central else dt_utc
        date_part = dt_local.strftime("%Y-%m-%d")
        time_part = dt_local.strftime("%I:%M %p").lstrip("0")
        tz_part = dt_local.tzname() or ("CT" if tz_central else "UTC")
        return f"{date_part} {time_part} {tz_part}"
    except Exception:
        return ""


def extract_event_info(event: dict) -> dict:
    """Extract event information into a structured dictionary."""
    name = event.get("name", "")
    ts = event.get("start_timestamp")
    if ts is None:
        ts = find_first_key(event, "start_timestamp")
    dt = central_time_from_timestamp(ts or 0)
    location = event.get("event_place", {}).get("contextual_name", "")
    details = (
        event.get("cover_photo", {}).get("photo", {}).get("accessibility_caption", "")
    )
    link = event.get("eventUrl", "")
    event_id = event.get("id", "")

    return {
        "name": name,
        "datetime": dt,
        "location": location,
        "details": details,
        "link": link,
        "event_id": event_id,
    }


def print_event_info(event: dict) -> None:
    """Print event information in the original text format."""
    info = extract_event_info(event)
    print(
        f'{info["name"]}\n{info["datetime"]}\n{info["location"]}\n"{info["details"]}"\n{info["link"]}\n{info["event_id"]}\n'
    )


def iter_event_nodes(obj):
    """Yield event-like dicts from an arbitrary nested structure.

    Heuristic: dicts with __typename == 'Event' or both 'name' and 'eventUrl',
    or 'name' and 'start_timestamp' (some payloads omit eventUrl at this level).
    """
    if isinstance(obj, dict):
        looks_like_event = (
            obj.get("__typename") == "Event"
            or ("name" in obj and "eventUrl" in obj)
            or ("name" in obj and "start_timestamp" in obj)
        )
        if looks_like_event:
            yield obj
        for v in obj.values():
            yield from iter_event_nodes(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_event_nodes(item)


def find_first_key(obj, key):
    """Recursively find the first non-null occurrence of a key in a nested structure."""
    if isinstance(obj, dict):
        if key in obj and obj[key] is not None:
            return obj[key]
        for v in obj.values():
            found = find_first_key(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first_key(item, key)
            if found is not None:
                return found
    return None


def main(
    debug: bool = False,
    har_path: str = "src/parser/Example2.har",
    output_format: str = "text",
):
    print("[har_parser] Starting...", flush=True)
    print(f"[har_parser] Using HAR: {har_path}", flush=True)
    hp = Path(har_path)
    if not hp.exists():
        print(f"[har_parser] ERROR: HAR file not found at {hp.resolve()}", flush=True)
        return None
    print("Hello")
    try:
        with open(har_path, "r", encoding="utf-8") as f:
            har = json.load(f)
    except Exception as e:
        print(f"Error loading HAR file '{har_path}': {e}")
        return None

    # Basic structure info (only show in text mode or debug)
    if output_format == "text" or debug:
        print("HAR file loaded successfully.", flush=True)
        print(f"Top-level HAR keys: {list(har.keys())}", flush=True)
    log = har.get("log", {})
    if output_format == "text" or debug:
        print(f"Log keys: {list(log.keys())}", flush=True)
    entries = log.get("entries", [])
    if output_format == "text" or debug:
        print(f"Number of entries: {len(entries)}", flush=True)
    if debug:
        print(f"Loaded HAR file with {len(entries)} entries.", flush=True)

    all_events = []  # Collect all events for JSON output

    for idx, entry in enumerate(entries):
        if debug:
            print(f"Entry {idx} keys: {list(entry.keys())}", flush=True)
        response = entry.get("response", {})
        content = response.get("content", {})
        text = content.get("text")
        if debug:
            if isinstance(text, str):
                print(f"Entry {idx} response text sample: {text[:200]}", flush=True)
            else:
                print(f"Entry {idx} missing response/content/text fields.", flush=True)
        if not text:
            continue

        # Parse the JSON string in the HAR content
        try:
            data = json.loads(text)
        except Exception as e:
            if debug:
                print(f"Entry {idx} JSON load error: {e}", flush=True)
            continue

        if debug:
            print(
                f"Entry {idx} parsed response JSON keys: {list(data.keys())}",
                flush=True,
            )

        # Prefer the known path; otherwise, fall back to recursive search
        events_printed = 0
        edges = (
            data.get("data", {})
            .get("viewer", {})
            .get("suggested_events", {})
            .get("events", {})
            .get("edges", [])
        )
        if isinstance(edges, list) and edges:
            if debug:
                print(
                    f"Entry {idx} found {len(edges)} event edges (direct path).",
                    flush=True,
                )
            for edge in edges:
                event = edge.get("node", {})
                if output_format == "json":
                    all_events.append(extract_event_info(event))
                else:
                    print_event_info(event)
                events_printed += 1
        else:
            if debug:
                print(
                    f"Entry {idx} falling back to recursive search for events…",
                    flush=True,
                )
            for node in iter_event_nodes(data):
                if output_format == "json":
                    all_events.append(extract_event_info(node))
                else:
                    print_event_info(node)
                events_printed += 1
        if debug:
            print(f"Entry {idx} printed {events_printed} events.", flush=True)

    if output_format == "json":
        print(json.dumps(all_events, indent=2))
        return all_events
    else:
        print("[har_parser] Done.", flush=True)
        return all_events


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract Facebook event data from a HAR file."
    )
    parser.add_argument(
        "--har",
        dest="har_path",
        default="src/parser/Example2.har",
        help="Path to HAR file (default: src/parser/Example2.har)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="Output format: text (default) or json",
    )
    args = parser.parse_args()

    # Make sure output is unbuffered; prints above already flush, but keep consistent
    sys.stdout.flush()
    main(debug=args.debug, har_path=args.har_path, output_format=args.output_format)
