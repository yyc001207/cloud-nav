import re
from typing import Optional
from datetime import datetime, timezone, timedelta


def to_camel(string: str) -> str:
    if "_" not in string:
        return string
    components = string.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def to_snake(string: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def mask_sensitive_data(data: dict, sensitive_fields: list) -> dict:
    masked = data.copy()
    for field in sensitive_fields:
        if field in masked:
            value = str(masked[field])
            if len(value) > 8:
                masked[field] = value[:4] + "****" + value[-4:]
            else:
                masked[field] = "****"
    return masked


def to_beijing_time(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    beijing_tz = timezone(timedelta(hours=8))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(beijing_tz)


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\/\\:*?"<>|]', "_", name)
