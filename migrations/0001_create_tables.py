"""
Create tables for location update, register and deregister events
"""

from typing import Any

from yoyo import step

__depends__ = {"0000_initial_schema"}

steps = [
    step(
        """
    CREATE TABLE vehicle.locationUpdate
    (
        id   VARCHAR(50),
        lat  FLOAT,
        long FLOAT,
        at   TIMESTAMP
    )
    """,
        """
    DROP TABLE vehicle.locationUpdate
    """,
    )
]
