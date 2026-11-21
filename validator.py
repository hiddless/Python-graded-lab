"""Row validation: airport list loading, single-row checks, record building."""
import re
import math
from datetime import datetime


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports = set()

    with open(path, "r", encoding="utf-8")as file:
        for line in file:
            code = line.strip()
            if code == "" or code.startswith("#"):
                continue
            airports.add(code)
    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len (fields) !=6:
        return "WRONG_FIELD_COUNT"    #this is for checking number of fields
    fields = [field.strip() for field in fields]
    if "" in fields:
        return "MISSING_FIELD"    # this is for checking öissing fields
    flight_id , origin, destination, departure, arrival, price = fields
    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id): #this is for checking flight id
        return "INVALID_FLIGHT_ID"
    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"   #Checking same airports
    date_format = "%Y-%m-%d %H:%M"       #for c hecking departure datetime

    try:
        departure_date = datetime.strptime(departure, date_format)    
        if departure_date.strftime(date_format) != departure:
            return "INVALID_DEPARTURE"
    except ValueError:
        return "INVALID_DEPARTURE"
    try:
        arrival_date = datetime.strptime(arrival, date_format)   #check arrival dateime 

        if arrival_date.strftime(date_format) != arrival:
            return "INVALID_ARRIVAL"
    except ValueError:
        return "INVALID_ARRIVAL"

    if arrival_date <= departure_date:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_value = float(price)
        if not math.isfinite(price_value):    #it checks if the price is non or infinity
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"
    if price_value <=0:
        return "NON_POSITIVE_PRICE"
    
    
    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime":fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5])
    }