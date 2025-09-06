import random
import string
from datetime import datetime, timedelta
from collections import OrderedDict
import time

def generate_node_id():
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return f"NODE-{random_chars}"

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_timestamp_gmt7():
    return (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

def get_current_timestamp_utc():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def format_response(status, message, data=None):
    response = OrderedDict()
    response["status"] = status
    response["message"] = message
    if data is not None:
        response["data"] = data
    return response

def validate_interval_input(input_str):
    try:
        interval = int(input_str)
        if interval <= 0:
            return False, "Interval must be greater than 0"
        return True, interval
    except ValueError:
        return False, "Please enter a valid number"