import bibliography_organizer as biborg
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="bibliography-organizer",
        description="A collection of tools to keep track of your references.",
    )
    commands = parser.add_subparsers(help="Commands", dest="command")

    status = commands.add_parser("status", help="Print status.")

    search = commands.add_parser("search", help="Full text search.")
    search.add_argument(
        "phrase",
        metavar="PHRASE",
        type=str,
        help=(
            "Run a full text search on the documents. "
            "Only for documents in the search-index."
        )
    )

    update = commands.add_parser(
        "update",
        help=(
            "Updates optical-character-recognition, icons, and search-index."
        )
    )
    update.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing cache."
    )


    args = parser.parse_args()

    if args.command == "status":
        biborg.Bibliography.print_status(bib_dir=os.getcwd())
    elif args.command == "search":
        search_instance = biborg.Search.Search(bib_dir=os.getcwd())
        search_results = search_instance.search(args.phrase)
        print(search_results)
    elif args.command == "update":
        biborg.bib_make_icons(
            bib_dir=os.getcwd(), overwrite_existing_output=args.overwrite
        )


if __name__ == "__main__":
    main()
