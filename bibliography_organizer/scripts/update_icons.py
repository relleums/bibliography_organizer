import bibliography_organizer as biborg
import argparse


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create or update icons."
            "An icon.jpg is a small rendering of the original's first page."
        )
    )
    parser.add_argument(
        "bibdir",
        metavar="DIR",
        type=str,
        help="path to bibliography directory",
    )
    parser.add_argument(
        "--overwrite",
        help="Overwrite existing icons, otherwise be lazy.",
    )
    args = parser.parse_args()
    biborg.bib_make_icons(
        bib_dir=args.bibdir,
        overwrite_existing_output=args.overwrite
    )

if __name__ == "__main__":
    main()
