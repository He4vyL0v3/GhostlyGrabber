from datetime import datetime


def adapt_datetime(val: datetime) -> str:
    return val.isoformat()


def convert_datetime(val: bytes) -> datetime:
    return datetime.fromisoformat(val.decode())
