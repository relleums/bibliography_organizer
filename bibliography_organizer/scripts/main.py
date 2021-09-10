import bibliography_organizer as biborg
import argparse
import os


def is_bibliography_dir(bib_dir):
    return os.path.exists(
        os.path.join(bib_dir, biborg.Bibliography.HIDDEN_WORK_DIRNAME)
    )


def print_warning_no_bibliography_dir(bib_dir):
    print(
        "Missing ",
        os.path.join(bib_dir, biborg.Bibliography.HIDDEN_WORK_DIRNAME),
        "\nMaybe this is not a bibliography directory?",
    )


def main():
    parser = argparse.ArgumentParser(
        prog="bib",
        description="Organize your digital library and references.",
    )
    commands = parser.add_subparsers(help="Commands", dest="command")

    init = commands.add_parser(
        "init", help="Initialize the bibliography-organizer in this directory."
    )

    status = commands.add_parser("status", help="Print the status.")

    search = commands.add_parser("search", help="Search in full text.")
    search.add_argument(
        "phrase",
        metavar="PHRASE",
        type=str,
        help=(
            "The phrase to search for. Use AND, OR, NOT and parantheses ()."
        ),
    )

    update = commands.add_parser(
        "update",
        help=(
            "Update optical-character-recognition (OCR), "
            "icons, and search-index."
        ),
    )

    export_bibtex = commands.add_parser(
        "export-bibtex",
        help=(
            "Export all reference.bib into a single file."
        ),
    )
    export_bibtex.add_argument(
        "path",
        metavar="PATH",
        type=str,
        help=(
            "The output-path of the bibtex-file."
        ),
    )

    args = parser.parse_args()
    bib_dir = os.getcwd()

    if args.command == "init":
        biborg.Bibliography.init(bib_dir=bib_dir)

    elif args.command == "status":
        if not is_bibliography_dir(bib_dir):
            print_warning_no_bibliography_dir(bib_dir)

        for entry_dir in biborg.Bibliography.list_entry_dirs(bib_dir=bib_dir):
            biborg.Entry.print_status(entry_dir)

    elif args.command == "search":
        if not is_bibliography_dir(bib_dir):
            print_warning_no_bibliography_dir(bib_dir)
            return

        search_instance = biborg.Index.Search(bib_dir=bib_dir)
        search_results = search_instance.search(args.phrase)

        for search_result in search_results:
            entry_dir = os.path.join(bib_dir, search_result["citekey"])
            biborg.Entry.print_overview(
                entry_dir, original_filename=search_result["original"]
            )

    elif args.command == "update":
        if not is_bibliography_dir(bib_dir):
            print_warning_no_bibliography_dir(bib_dir)
            return

        entry_dirs = biborg.Bibliography.list_entry_dirs(bib_dir=bib_dir)
        for entry_dir in entry_dirs:
            biborg.Entry.make_icon(entry_dir=entry_dir)
            biborg.Entry.update_optical_character_recognition(
                entry_dir=entry_dir
            )
        biborg.Index.increment_index(bib_dir=bib_dir)

    elif args.command == "export-bibtex":
        if not is_bibliography_dir(bib_dir):
            print_warning_no_bibliography_dir(bib_dir)
            return

        bib_str = biborg.Bibtex.make_bib_file(bib_dir=bib_dir)
        with open(args.path, "wt") as f:
            f.write(bib_str)

if __name__ == "__main__":
    main()
