"""swpy command line: list and fetch SWPy datasets.

Usage:
  swpy datasets [--files | --tables]
  swpy list DATA_ID [--start T] [--end T]
  swpy get DATA_ID [--start T] [--end T] [-o DIR]
  swpy table TABLE
  swpy csv TABLE [--start T] [--end T] [--columns a,b] [-o FILE]

Server, mode and storage root come from --server/--mode/--storage-root or
SWPY_SERVER / SWPY_MODE / SWPY_STORAGE_ROOT. Times are ISO-8601, UTC.
"""

import argparse
import json
import sys

import requests

from swpy.client import Client


def _parser():
    parser = argparse.ArgumentParser(prog="swpy", description="SWPy data access")
    parser.add_argument("--server", help="distribution server URL (SWPY_SERVER)")
    parser.add_argument("--mode", choices=["api", "direct"], help="transfer mode (SWPY_MODE)")
    parser.add_argument("--storage-root", help="local storage root for direct mode")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("datasets", help="list datasets")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--files", action="store_true", help="file datasets only")
    group.add_argument("--tables", action="store_true", help="table datasets only")

    for name, text in (("list", "list a file dataset's files"),
                       ("get", "fetch a file dataset's files")):
        p = sub.add_parser(name, help=text)
        p.add_argument("data_id")
        p.add_argument("--start")
        p.add_argument("--end")
        if name == "get":
            p.add_argument("-o", "--output", default=".", help="destination directory (api mode)")

    p = sub.add_parser("table", help="show a table's columns and time range")
    p.add_argument("table")

    p = sub.add_parser("csv", help="export a table as CSV")
    p.add_argument("table")
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--columns", help="comma-separated column subset")
    p.add_argument("-o", "--output", help="output file")
    return parser


def _run(args):
    client = Client(server=args.server, mode=args.mode, storage_root=args.storage_root)
    if args.command == "datasets":
        found = client.datasets()
        if not args.tables:
            for d in found["files"]:
                detail = " ".join(f"{k}={v}" for k, v in d.items()
                                  if k not in ("data_id", "source", "file_format"))
                print(f"file   {d['data_id']:<36} {detail}")
        if not args.files:
            for t in found["tables"]:
                print(f"table  {t['table']:<36} time={t['time_column']}")
    elif args.command == "list":
        entries = client.files(args.data_id, args.start, args.end)
        for e in entries:
            print(f"{e['time']}  {e['size'] or '':>12}  {e.get('local', e['path'])}")
        print(f"{len(entries)} files", file=sys.stderr)
    elif args.command == "get":
        paths = client.get(args.data_id, args.start, args.end, dest=args.output)
        for path in paths:
            print(path)
        verb = "located" if client.mode == "direct" else "downloaded"
        print(f"{len(paths)} files {verb}", file=sys.stderr)
    elif args.command == "table":
        print(json.dumps(client.table_info(args.table), indent=2))
    elif args.command == "csv":
        columns = args.columns.split(",") if args.columns else None
        print(client.csv(args.table, args.start, args.end, columns, args.output))


def main():
    """Entry point; server errors are reported without a traceback."""
    args = _parser().parse_args()
    try:
        _run(args)
    except requests.HTTPError as exc:
        try:
            detail = exc.response.json().get("detail")
        except ValueError:
            detail = exc.response.text
        sys.exit(f"swpy: server error {exc.response.status_code}: {detail}")
    except (requests.ConnectionError, ValueError, FileNotFoundError) as exc:
        sys.exit(f"swpy: {exc}")


if __name__ == "__main__":
    main()
