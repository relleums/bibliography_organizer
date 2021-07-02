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

    update = commands.add_parser('icons', help='Update icons in entries.')
    update.add_argument('--overwrite', action="store_true", help='Overwrite existing icons.')

    update = commands.add_parser('ocr', help='Run optical character recognition.')
    update.add_argument('--overwrite', action="store_true", help='Overwrite existing ocrs.')

    args = parser.parse_args()

    if args.command == "status":
        biborg.bib_print_status(bib_dir=os.getcwd())
    elif args.command == "icons":
        biborg.bib_make_icons(
            bib_dir=os.getcwd(),
            overwrite_existing_output=args.overwrite
        )
    elif args.command == "ocr":
        biborg.bib_make_ocr(
            bib_dir=os.getcwd(),
            overwrite_existing_output=args.overwrite
        )

if __name__ == "__main__":
    main()





