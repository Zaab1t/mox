import pytz
from datetime import datetime
from dateutil import parser

def parse_time(time_string):
    if time_string == '-infinity':
        return pytz.utc.localize(datetime.min)
    elif time_string == 'infinity':
        return pytz.utc.localize(datetime.max)
    else:
        return parser.parse(time_string)

def unparse_time(dt):
    if dt == pytz.utc.localize(datetime.min):
        return '-infinity'
    elif dt == pytz.utc.localize(datetime.max):
        return 'infinity'
    else:
        return dt.isoformat()
