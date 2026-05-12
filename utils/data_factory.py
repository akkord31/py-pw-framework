from __future__ import annotations

import random
import string
import uuid
from datetime import datetime


def random_string(length: int = 8, prefix: str = "") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase, k=length))
    return f"{prefix}{suffix}"


def random_email(domain: str = "test.local") -> str:
    return f"{random_string(8)}@{domain}"


def unique_username(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
