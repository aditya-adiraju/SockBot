# Module to enable timestamped logs
from datetime import datetime
from pytz import utc, timezone

class LOG_LEVEL:
    ERROR = 'ERR'
    INFO  = 'INF'
    DEBUG = 'DBG'

def _generate_timestamp() -> str:
    date_format = "%d-%b-%Y %H:%M:%S"
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

def _log(log_level: str, *values: object, sep: str | None = " ", end: str | None = "\n") -> None:
    print(f"[{log_level}][{_generate_timestamp()}]", *values, sep=sep, end=end)
    with open('log.txt', 'a') as log_file:
        print(f"[{log_level}] [{_generate_timestamp()}]", *values, sep=sep, end=end, file=log_file)

def error(*values: object, sep: str | None = " ", end: str | None = "\n") -> None:
    _log(LOG_LEVEL.ERROR, *values, sep=sep, end=end)

def info(*values: object, sep: str | None = " ", end: str | None = "\n") -> None:
    _log(LOG_LEVEL.INFO, *values, sep=sep, end=end)

def debug(*values: object, sep: str | None = " ", end: str | None = "\n") -> None:
    _log(LOG_LEVEL.DEBUG, *values, sep=sep, end=end)

