"""
Create vehicle schema
"""

from typing import Any
from yoyo import step

__depends__: Any = {}

steps = [step("CREATE SCHEMA vehicle", "DROP SCHEMA vehicle")]