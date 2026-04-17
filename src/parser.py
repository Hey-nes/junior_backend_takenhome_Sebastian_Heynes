from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup


@dataclass
class ParsedQueueSpot:
    queue_type: str
    registration_date: str
    last_updated: str
    update_before: str
    status: str
    inactive_reason: Optional[str]


def parse_queue_spots(html: str) -> list[ParsedQueueSpot]:
    # Initialize parser and find queue cards
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article", class_="queue-card")

    parsed_queue_spots = []

    # Map inconsistent labels to dataclass fields
    label_map = {
        "registration date": "registration_date",
        "reg. date": "registration_date",
        "last updated": "last_updated",
        "updated": "last_updated",
        "update before": "update_before",
        "please refresh before": "update_before",
        "status": "status",
    }

    for card in cards:
        extracted_data = {}

        queue_type = card.find("div", class_="queue-title").get_text(strip=True)

        items = card.find_all("div", class_="item")
        for item in items:
            label = item.find("div", class_="label").get_text(strip=True).lower()
            value = item.find("div", class_="value").get_text(strip=True)

            # Unify label names and normalize status casing
            if label in label_map:
                field_name = label_map[label]
                if field_name == "status":
                    value = value.lower().strip()

                extracted_data[field_name] = value

        # Handle optional inactive reason
        inactive_reason = None
        divider = card.find("div", class_="divider")
        if divider:
            reason_value = divider.find("div", class_="value")
            inactive_reason = (
                reason_value.get_text(strip=True) if reason_value else None
            )

        spot = ParsedQueueSpot(
            queue_type=queue_type,
            registration_date=extracted_data.get("registration_date", ""),
            last_updated=extracted_data.get("last_updated", ""),
            update_before=extracted_data.get("update_before", ""),
            status=extracted_data.get("status", ""),
            inactive_reason=inactive_reason,
        )

        parsed_queue_spots.append(spot)

    return parsed_queue_spots
