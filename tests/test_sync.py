import pytest
from src.parser import parse_queue_spots, ParsedQueueSpot

def test_parse_queue_spots_handles_inconsistent_labels():
    mock_html = """
    <article class="queue-card">
        <div class="queue-title">Youth Housing</div>
        <div class="item">
            <div class="label">Reg. date</div>
            <div class="value">2024-01-01</div>
        </div>
        <div class="item">
            <div class="label">Status</div>
            <div class="value">ACTIVE </div>
        </div>
    </article>
    """

    # Run the parser on mock HTML
    results = parse_queue_spots(mock_html)

    # Sanity check
    assert len(results) == 1
    spot = results[0]
    
    assert spot.queue_type == "Youth Housing"
    # Verify the mapper translated "Reg. date" to "registration_date"
    assert spot.registration_date == "2024-01-01"
    # Verify the status was normalized to lowercase and stripped
    assert spot.status == "active"

def test_parsed_queue_spot_dto_structure():
    # Verify the DTO (Dataclass) works as expected
    spot = ParsedQueueSpot(
        queue_type="General",
        registration_date="2023-12-01",
        last_updated="2024-01-01",
        update_before="2024-02-01",
        status="active",
        inactive_reason=None
    )
    assert spot.queue_type == "General"
    assert spot.inactive_reason is None