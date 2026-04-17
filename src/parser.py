from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class ParsedQueueSpot:
    queue_type: str
    registration_date: str
    last_updated: str
    update_before: str
    status: str
    inactive_reason: Optional[str]


# Map inconsistent labels to dataclass fields
_LABEL_MAP = {
    "registration date": "registration_date",
    "reg. date": "registration_date",
    "last updated": "last_updated",
    "updated": "last_updated",
    "update before": "update_before",
    "please refresh before": "update_before",
    "status": "status",
}


def _parse_card(card: Tag) -> ParsedQueueSpot:
    extracted_data = {}

    title_element = card.find("div", class_="queue-title")
    # Check if title element exists before extracting text
    queue_type = (
        title_element.get_text(strip=True) if title_element else "Unknown Queue"
    )

    items = card.find_all("div", class_="item")
    for item in items:
        label_el = item.find("div", class_="label")
        value_el = item.find("div", class_="value")

        # Check if both label and value elements exist before extracting text
        if label_el and value_el:
            label = label_el.get_text(strip=True).lower()
            value = value_el.get_text(strip=True)

            # Unify label names and normalize status casing
            if label in _LABEL_MAP:
                field_name = _LABEL_MAP[label]
                if field_name == "status":
                    value = value.lower().strip()

                extracted_data[field_name] = value

    # Handle optional inactive reason
    inactive_reason = None
    divider = card.find("div", class_="divider")
    if divider:
        reason_value = divider.find("div", class_="value")
        inactive_reason = reason_value.get_text(strip=True) if reason_value else None

    return ParsedQueueSpot(
        queue_type=queue_type,
        registration_date=extracted_data.get("registration_date", ""),
        last_updated=extracted_data.get("last_updated", ""),
        update_before=extracted_data.get("update_before", ""),
        status=extracted_data.get("status", ""),
        inactive_reason=inactive_reason,
    )


def parse_queue_spots(html: str) -> list[ParsedQueueSpot]:
    # Initialize parser and find queue cards
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article", class_="queue-card")

    # Return the parsed version of each card in a list
    return [_parse_card(card) for card in cards]
