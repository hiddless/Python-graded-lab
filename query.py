"""Running queries against the flight database."""


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    allowed_keys = [
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price"
    ]

    #we need to check unknown query keys
    for key in query:
        if key not in allowed_keys:
            return{
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            }
    matches = []

    for flight in db:
        match = True
        for key, value in query.items():
            if key =="departure_datetime":
                if flight[key] < value:
                    match = False
            elif key == "arrival_datetime":
                if flight[key] > value:
                    match =False
            elif key == "price":
                if flight[key] > value:
                    match = False
            else:
                if flight[key] != value:
                    match = False

        if match: 
            matches.append(flight)
    return {
        "query": query,
        "matches": matches
    }
    


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]
    results = []

    for query in queries:
        results.append(run_query(db, query))
    return results
    
