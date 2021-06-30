import bibliography_organizer as biborg
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Print status of bibliography."
    )
    parser.add_argument(
        "bibdir",
        metavar="DIR",
        type=str,
        help="path to bibliography directory",
    )
    args = parser.parse_args()
    biborg.bib_print_status(args.bibdir)


if __name__ == "__main__":
    main()