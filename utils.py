# Utility functions for time and status formatting

from datetime import datetime, timedelta

def str_to_time(timestr):
    """
    Convert a string 'HH:MM' or 'HH:MM AM/PM' to a datetime.time object.
    """
    try:
        return datetime.strptime(timestr, '%H:%M').time()
    except ValueError:
        return datetime.strptime(timestr, '%I:%M %p').time()

def add_minutes_to_time(time_obj, minutes):
    """
    Adds minutes to a datetime.time object, returns a new datetime.time.
    """
    full_datetime = datetime.combine(datetime.today(), time_obj) + timedelta(minutes=minutes)
    return full_datetime.time()

def time_to_str(time_obj):
    """
    Format a datetime.time object as a string HH:MM AM/PM.
    """
    return time_obj.strftime('%I:%M %p').lstrip('0')

def format_package_status(package):
    """
    Returns a string describing the status of a package, including delivery time if applicable.
    package is expected to have fields:
    - id
    - address
    - deadline
    - city
    - zip_code
    - weight
    - status (At Hub / En Route / Delivered)
    - delivery_time (None or datetime.time)
    """
    status_str = f"Package {package['id']} to {package['address']} - Deadline: {package['deadline']} - Status: {package['status']}"
    if package['delivery_time']:
        status_str += f" at {time_to_str(package['delivery_time'])}"
    return status_str
