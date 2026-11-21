"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import os
import csv
import json
import argparse
import logging
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB089"
FIRST_NAME = "Duru"
LAST_NAME = "Karaagac"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-i", help="Input CSV file")
    group.add_argument("-d", help="Input CSV folder")
    group.add_argument("-j", help="Existing JSON database")

    parser.add_argument("-a", help="Airport list")
    parser.add_argument("-o", help="Output JSON file")
    parser.add_argument("-q", help="Query JSON file")
    parser.add_argument("-r", default=".", help="Response folder")

    try:
        args= parser.parse_args(argv)
        if (args.i or args.d) and not args.a:
            parser.error("-a is required with -i or -d")
        if args.j and args.o:
            parser.error("-o cant be used with -j")
    except SystemExit as error:
        return int(error.code)
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    # TODO: load or parse the data, write the database and errors.log.
    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db =json.load(file)

                if not isinstance(db, list):
                    raise ValueError ("Invalid database")
                for record in db:
                    if not isinstance(record, dict):
                        raise ValueError("Invalid database")
        else:
            airports= load_airports(args.a)

            if args.i:
                paths= [args.i]
            else:
                paths =[]
                for filename in sorted(os.listdir(args.d)):
                    path = os.path.join(args.d,filename)

                    if filename.endswith(".csv") and os.path.isfile(path):
                        paths.append(path)
                if not paths:
                    raise ValueError("No CSV files found")
            db, errors = parse_files(paths, airports)
            #json db
            output = args.o if args.o else "db.json"

            with open(output, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=4)

            #write errors.log
            log_folder = os.path.dirname(output) or "."
            log_path = os.path.join(log_folder, "errors.log")

            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(handler)
            for error in errors:
                logger.warning(error)
            
            
    # TODO: run the queries and write the response file.
        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, (dict,list)):
                raise ValueError("Invalid query file")
            if isinstance(queries, list):
                for query in queries:
                    if not isinstance(query, dict):
                        raise ValueError("Invalid query file")
            results = run_queries(db, queries)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = os.path.join(args.r, filename)

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4)
        return 0
    except (OSError, ValueError, TypeError,KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()

    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    
if __name__ == "__main__":
    sys.exit(main())
