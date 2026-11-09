"""Business datetimes use Beijing wall-clock time; JWT timestamps remain UTC."""

from datetime import datetime

import pytz

BEIJING = pytz.timezone("Asia/Shanghai")


def beijing_now():
    return datetime.now(BEIJING).replace(tzinfo=None)


def format_beijing(value, pattern="%Y-%m-%d %H:%M:%S"):
    # Existing naive database values already represent Beijing time.
    if value.tzinfo is not None:
        value = value.astimezone(BEIJING)
    return value.strftime(pattern)
