import bibliography_organizer as biborg
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="bibliography-organizer",
        description="A collection of tools to keep track of your references."
    )
    commands = parser.add_subparsers(help='Commands', dest="command")

    status = commands.add_parser('status', help='Print status.')

    update = commands.add_parser('icons', help='Update entries.')
    update.add_argument('--overwrite', action="store_true", help='Overwrite existing icons')

    args = parser.parse_args()

    if args.command == "status":
        biborg.bib_print_status(bib_dir=os.getcwd())
    elif args.command == "icons":
        biborg.bib_make_icons(
            bib_dir=os.getcwd(),
            overwrite_existing_output=args.overwrite
        )

if __name__ == "__main__":
    main()





