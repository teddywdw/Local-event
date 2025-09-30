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
    """Convert epoch seconds (UTC) to America/Chicago local time, formatted.

    Example format: 'Saturday at 9 PM' (no date), matching the user's example.
    """
    try:
        dt_utc = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        dt_ct = dt_utc.astimezone(ZoneInfo("America/Chicago"))
        return dt_ct.strftime("%A at %I %p").lstrip("0").replace(" 0", " ")
    except Exception:
        return ""


def print_event_info(event: dict) -> None:
    name = event.get("name", "")
    dt = central_time_from_timestamp(event.get("start_timestamp", 0))
    location = event.get("event_place", {}).get("contextual_name", "")
    # Best-effort for host. Often not present in this payload; fall back to location or blank
    event_by = (
        event.get("event_host", "") or event.get("owner", {}).get("name", "") or ""
    )
    details = (
        event.get("cover_photo", {}).get("photo", {}).get("accessibility_caption", "")
    )
    link = event.get("eventUrl", "")
    event_id = event.get("id", "")
    print(f'{name}\n{dt}\n{location}\n{event_by}\n"{details}"\n{link}\n{event_id}\n')


def iter_event_nodes(obj):
    """Yield event-like dicts from an arbitrary nested structure.

    Heuristic: dicts with __typename == 'Event' or both 'name' and 'eventUrl'.
    """
    if isinstance(obj, dict):
        if obj.get("__typename") == "Event" or ("name" in obj and "eventUrl" in obj):
            yield obj
        for v in obj.values():
            yield from iter_event_nodes(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_event_nodes(item)


def main(debug: bool = False, har_path: str = "src/Example2.har"):
    print("[har_parser] Starting...", flush=True)
    print(f"[har_parser] Using HAR: {har_path}", flush=True)
    hp = Path(har_path)
    if not hp.exists():
        print(f"[har_parser] ERROR: HAR file not found at {hp.resolve()}", flush=True)
        return
    print("Hello")
    try:
        with open(har_path, "r", encoding="utf-8") as f:
            har = json.load(f)
    except Exception as e:
        print(f"Error loading HAR file '{har_path}': {e}")
        return

    # Basic structure info
    print("HAR file loaded successfully.", flush=True)
    print(f"Top-level HAR keys: {list(har.keys())}", flush=True)
    log = har.get("log", {})
    print(f"Log keys: {list(log.keys())}", flush=True)
    entries = log.get("entries", [])
    print(f"Number of entries: {len(entries)}", flush=True)
    if debug:
        print(f"Loaded HAR file with {len(entries)} entries.", flush=True)

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
                print_event_info(event)
                events_printed += 1
        else:
            if debug:
                print(
                    f"Entry {idx} falling back to recursive search for events…",
                    flush=True,
                )
            for node in iter_event_nodes(data):
                print_event_info(node)
                events_printed += 1
        if debug:
            print(f"Entry {idx} printed {events_printed} events.", flush=True)
    print("[har_parser] Done.", flush=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract Facebook event data from a HAR file."
    )
    parser.add_argument(
        "--har",
        dest="har_path",
        default="src/Example2.har",
        help="Path to HAR file (default: src/Example2.har)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    # Make sure output is unbuffered; prints above already flush, but keep consistent
    sys.stdout.flush()
    main(debug=args.debug, har_path=args.har_path)
