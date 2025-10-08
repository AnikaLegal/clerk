from datetime import datetime, date


def string_to_date(date_string: str, format: str = "%Y-%m-%d") -> date | None:
    return datetime.strptime(date_string, format).date() if date_string else None
