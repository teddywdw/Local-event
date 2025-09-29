import json
from haralyzer import HarParser

def find_event_names(obj, found_events):
    """
    Recursively search for event 'name' fields in any dict/list structure.
    Only adds names where the parent dict looks like an event node.
    """
    if isinstance(obj, dict):
        # Heuristic: looks like an event node if it has 'name' and 'eventUrl' or '__typename' == 'Event'
        if (
            "name" in obj
            and (
                "eventUrl" in obj
                or obj.get("__typename") == "Event"
            )
        ):
            found_events.append(obj["name"])
        # Continue searching all values
        for v in obj.values():
            find_event_names(v, found_events)
    elif isinstance(obj, list):
        for item in obj:
            find_event_names(item, found_events)

def parse_facebook_har(har_file_path):
    """
    Parses a HAR file to extract all event names from Facebook GraphQL API calls.
    """
    try:
        print(f"The file '{har_file_path}' was found.")
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.loads(f.read())
    except FileNotFoundError:
        print(f"Error: The file '{har_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{har_file_path}' is not a valid JSON file.")
        return

    parser = HarParser(har_data)

    # Collect all entries from all pages
    all_entries = []
    for page in parser.pages:
        all_entries.extend(page.entries)
    # Also add top-level entries (in case there are no pages)
    if hasattr(parser, "entries"):
        all_entries.extend(parser.entries)

    # Filter entries to find the GraphQL requests
    graphql_entries = [
        entry for entry in all_entries
        if "api/graphql/" in entry.request.url and entry.request.method == 'POST'
    ]

    if not graphql_entries:
        print("No GraphQL API requests found in the HAR file.")
        return

    all_event_names = []

    for entry in graphql_entries:
        if entry.response and hasattr(entry.response, "text") and entry.response.text:
            try:
                # Some GraphQL responses may be a list of JSON objects
                response_text = entry.response.text
                try:
                    response_json = json.loads(response_text)
                except json.JSONDecodeError:
                    # Sometimes the response is multiple JSON objects concatenated
                    # Try to split and parse each
                    response_json = []
                    for part in response_text.split('\n'):
                        part = part.strip()
                        if part:
                            try:
                                response_json.append(json.loads(part))
                            except Exception:
                                continue
                find_event_names(response_json, all_event_names)
            except Exception:
                continue

    if all_event_names:
        print("All events found in the HAR file:")
        for name in sorted(set(all_event_names)):
            print(f" - {name}")
    else:
        print("No events found in the HAR file.")

# Run the parser on your HAR file
parse_facebook_har('src/Example2.har')
