# Data Contract: HAR Parser Output

## Overview
This document defines the data contract between the HAR parser (`Local-event`) and future web applications that will consume its output.

## Usage Examples

### Command Line Interface
```powershell
# Text output (default - for human reading)
python src/har_parser.py --har src/Example2.har --format text

# JSON output (for programmatic consumption)
python src/har_parser.py --har src/Example2.har --format json

# Debug mode (shows processing details)
python src/har_parser.py --har src/Example2.har --format json --debug
```

### Programmatic Usage (Python Module)
```python
# Import and use as a module
from src.har_parser import main

# Get structured data
events = main(debug=False, har_path="src/Example2.har", output_format="json")
# Returns: List[Dict] with event objects
```

## JSON Output Schema

### Array of Event Objects
```json
[
  {
    "name": "Event Name",
    "datetime": "2025-10-04 9:00 PM CDT",
    "location": "Venue Address",
    "details": "Cover photo description or details",
    "link": "https://www.facebook.com/events/123456789/",
    "event_id": "123456789"
  }
]
```

### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | `string` | Event title/name | `"Old Fashioned Month at Pour"` |
| `datetime` | `string` | Central Time formatted date with DST awareness | `"2025-10-04 9:00 PM CDT"` |
| `location` | `string` | Venue name and/or address | `"4400 S 70th St #100, Lincoln, NE"` |
| `details` | `string` | Cover photo accessibility caption or description | `"May be an image of 1 person..."` |
| `link` | `string` | Facebook event URL | `"https://www.facebook.com/events/3095428473996911/"` |
| `event_id` | `string` | Facebook event ID | `"3095428473996911"` |

## Integration for Web Applications

### Option A: CLI Integration (Recommended for MVP)
```python
import subprocess
import json

def get_events_from_har(har_file_path):
    """Extract events using the CLI tool"""
    result = subprocess.run([
        'python', 'path/to/Local-event/src/har_parser.py',
        '--har', har_file_path,
        '--format', 'json'
    ], capture_output=True, text=True, cwd='path/to/Local-event')

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"Parser failed: {result.stderr}")
```

### Option B: Module Import
```python
import sys
sys.path.append('path/to/Local-event/src')
from har_parser import main

def get_events_from_har(har_file_path):
    """Extract events using direct module import"""
    return main(debug=False, har_path=har_file_path, output_format="json")
```

## Error Handling

### Return Values
- **Success**: Returns list of event dictionaries (even if empty list)
- **File Not Found**: Returns `None` and prints error message
- **JSON Parse Error**: Skips problematic entries, continues processing
- **No Events Found**: Returns empty list `[]`

### Error Detection
```python
events = get_events_from_har("file.har")
if events is None:
    # File error occurred
    handle_file_error()
elif len(events) == 0:
    # No events found (valid but empty result)
    handle_no_events()
else:
    # Success: process events
    display_events(events)
```

## Timezone Handling
- All timestamps are converted to **America/Chicago** timezone
- Automatic DST detection (CDT vs CST)
- Format: `"YYYY-MM-DD H:MM AM/PM CDT/CST"`
- Fallback to UTC if timezone data unavailable

## Compatibility Notes
- **Python 3.8+** required
- **Windows**: Requires `tzdata` package for timezone support
- **Dependencies**: `haralyzer`, `tzdata` (see `requirements.txt`)
- **Encoding**: UTF-8 input/output, handles Unicode characters

## Sample Output
```json
[
  {
    "name": "Old Fashioned Month at Pour",
    "datetime": "2025-10-04 9:00 PM CDT",
    "location": "4400 S 70th St #100, Lincoln, NE, United States, Nebraska 68516",
    "details": "May be an image of 1 person, drink and text that says 'OLD FASHIONED MONTH only at Pour POUR CRAFT BEER CRAFTBEER&SPIRITS & SPIRITS EVERY SATURDAY IN OCT TRY 3 NEW OLD FASHIONEDS!'",
    "link": "https://www.facebook.com/events/3095428473996911/",
    "event_id": "3095428473996911"
  }
]
```

This contract ensures clean separation between the HAR parsing logic and any web applications that consume the event data.
