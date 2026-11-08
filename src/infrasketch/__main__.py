"""``python -m infrasketch search <words>`` prints the import to use."""

from __future__ import annotations

import argparse
import sys

from infrasketch.search import categories, search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="infrasketch",
        description="Find Azure and AWS resource classes and draw architecture diagrams.",
    )
    sub = parser.add_subparsers(dest="command")

    find = sub.add_parser("search", help="Find a resource by name")
    find.add_argument("query", nargs="+", help="Words to match, such as: managed redis")

    listed = sub.add_parser("categories", help="List resource categories")
    listed.set_defaults(command="categories")

    args = parser.parse_args(argv)
    if args.command == "search":
        hits = search(" ".join(args.query))
        if not hits:
            print("No matching resources.")
            return 1
        for hit in hits:
            print(hit)
            print()
        print(f"{len(hits)} match{'es' if len(hits) != 1 else ''}.")
        return 0
    if args.command == "categories":
        for name in categories():
            print(name)
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
