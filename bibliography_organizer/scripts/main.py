import bibliography_organizer as biborg
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="bibliography-organizer",
        description="A collection of tools to keep track of your references.",
    )
    commands = parser.add_subparsers(help="Commands", dest="command")

    init = commands.add_parser(
        "init", help="Initialize the bibliography-organizer."
    )

    status = commands.add_parser("status", help="Print status.")

    search = commands.add_parser("search", help="Full text search.")
    search.add_argument(
        "phrase",
        metavar="PHRASE",
        type=str,
        help=(
            "Run a full text search on the documents. "
            "Only for documents in the search-index."
        ),
    )

    update = commands.add_parser(
        "update",
        help=(
            "Updates optical-character-recognition, icons, and search-index."
        ),
    )

    args = parser.parse_args()
    bib_dir = os.getcwd()

    if args.command == "init":
        biborg.Bibliography.init(bib_dir=bib_dir)

    elif args.command == "status":
        for entry_dir in biborg.Bibliography.list_entry_dirs(bib_dir=bib_dir):
            biborg.Entry.print_status(entry_dir)

    elif args.command == "search":
        search_instance = biborg.Index.Search(bib_dir=bib_dir)
        search_results = search_instance.search(args.phrase)

        for search_result in search_results:
            entry_dir = os.path.join(bib_dir, search_result["citekey"])
            biborg.Entry.print_overview(
                entry_dir, original_filename=search_result["original"]
            )

    elif args.command == "update":
        entry_dirs = biborg.Bibliography.list_entry_dirs(bib_dir=bib_dir)
        for entry_dir in entry_dirs:
            biborg.Entry.make_icon(entry_dir=entry_dir)
            biborg.Entry.update_optical_character_recognition(
                entry_dir=entry_dir
            )
        biborg.Index.increment_index(bib_dir=bib_dir)


if __name__ == "__main__":
    main()
