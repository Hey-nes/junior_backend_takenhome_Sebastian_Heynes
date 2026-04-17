from __future__ import annotations

import os
from datetime import datetime, UTC

from database import get_connection, get_user_id, update_last_login, update_queue_spot
from parser import parse_queue_spots
from platform_client import build_session

TARGET_USER = "Maxim Eyd"


def main() -> None:
    base_url = os.getenv("PLATFORM_BASE_URL", "http://127.0.0.1:8000")
    username = os.getenv("PLATFORM_USERNAME", "maxim@example.com")
    password = os.getenv("PLATFORM_PASSWORD", "test123")
    db_path = os.getenv("DB_PATH", "./data/app.db")

    platform = build_session(base_url)
    platform.login(username=username, password=password)
    html = platform.fetch_account_html()
    queue_spots = parse_queue_spots(html)

    if not queue_spots:
        raise RuntimeError("No queue spots were parsed from the page.")

    with get_connection(db_path) as connection:
        user_id = get_user_id(connection, TARGET_USER)
        if user_id is None:
            raise RuntimeError(f"Could not find user: {TARGET_USER}")

        login_timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
        update_last_login(connection, user_id, login_timestamp)

        for spot in queue_spots:
            update_queue_spot(
                connection=connection,
                user_id=user_id,
                queue_type=spot.queue_type,
                registration_date=spot.registration_date,
                last_updated=spot.last_updated,
                update_before=spot.update_before,
                status=spot.status,
                inactive_reason=spot.inactive_reason,
            )

    # Re-fetch the data and print out a rapport
    with get_connection(db_path) as connection:
        updated_spots = connection.execute(
            "SELECT * FROM queue_spots WHERE user_id = ?", (user_id,)
        ).fetchall()

        print(f"Updated the following {len(queue_spots)} queue spots:")

        for row in updated_spots:
            print(f"\n[{row['queue_type']} Queue]")
            print(f"  Registration Date: {row['registration_date']}")
            print(f"  Last Updated:      {row['last_updated']}")
            print(f"  Update Before:     {row['update_before']}")
            print(f"  Status:            {row['status'].upper()}")

            if row["inactive_reason"]:
                print(f"  Inactive Reason:   {row['inactive_reason']}")

        user_row = connection.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        if user_row:
            print(f"\n[User Affected]")
            print(f"  {TARGET_USER}")
            print(f"  Last Login:        {user_row['last_login']}")


if __name__ == "__main__":
    main()
