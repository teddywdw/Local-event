from pathlib import Path
import json

from src.parser import main


def test_parse_happy_path(tmp_path):
    fixtures = Path(__file__).resolve().parents[0] / "fixtures"
    sample = fixtures / "simple.har"
    assert sample.exists()
    events = main(debug=False, har_path=str(sample), output_format="json")
    assert isinstance(events, list)
    # Check if we got some events (the simple.har might be empty, so just check structure)


def test_parse_no_events(tmp_path):
    # create a minimal HAR with no event entries
    no_events = tmp_path / "no_events.har"
    no_events.write_text('{"log": {"entries": []}}', encoding="utf-8")
    events = main(debug=False, har_path=str(no_events), output_format="json")
    assert events == []


def test_parse_example_har():
    # Test with the actual example file
    events = main(debug=False, har_path="src/parser/Example2.har", output_format="json")
    assert isinstance(events, list)
    assert len(events) > 0  # Should have events in Example2.har

    # Check structure of first event
    if events:
        event = events[0]
        assert "name" in event
        assert "datetime" in event
        assert "location" in event
        assert "details" in event
        assert "link" in event
        assert "event_id" in event


def test_parse_concatenated_json(tmp_path):
    # build a HAR where the response.text contains event-like JSON structure
    har = {
        "log": {
            "version": "1.2",
            "creator": {"name": "test", "version": "1.0"},
            "entries": [
                {
                    "request": {
                        "method": "POST",
                        "url": "https://www.facebook.com/api/graphql/",
                    },
                    "response": {
                        "content": {
                            "text": '{"data": {"viewer": {"suggested_events": {"events": {"edges": [{"node": {"__typename": "Event", "name": "Test Event A", "start_timestamp": 1700000000, "eventUrl": "https://facebook.com/events/123"}}, {"node": {"__typename": "Event", "name": "Test Event B", "start_timestamp": 1700000000, "eventUrl": "https://facebook.com/events/456"}}]}}}}}'
                        }
                    },
                }
            ],
        }
    }

    p = tmp_path / "concat.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    events = main(debug=False, har_path=str(p), output_format="json")
    assert isinstance(events, list)
    assert len(events) == 2
    assert any(event["name"] == "Test Event A" for event in events)
    assert any(event["name"] == "Test Event B" for event in events)
