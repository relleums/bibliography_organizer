import os
import glob
from . import Status
from . import Bibtex
from . import Entry
from . import Index


def list_entry_dirs(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    entry_dirs = glob.glob(os.path.join(bib_dir, "*"))
    entry_dirs.sort()
    return entry_dirs


def init(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    os.makedirs(os.path.join(bib_dir, ".bibliography_organizer"))
    with open(os.path.join(bib_dir, ".gitignore"), "wt") as f:
        f.write("icon.jpg\n")
        f.write("ocr\n")

    index_dir = Index.get_index_dir(bib_dir)
    os.makedirs(index_dir)
    Index.make_clean_index(bib_dir=bib_dir)


def print_status(bib_dir):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)

    if len(entry_dirs):
        for entry_dir in entry_dirs:
            Entry.print_status(entry_dir)
    else:
        print("No entries in '{:s}'".format(bib_dir))
        print("Maybe thit is not a bibliography directory?")


def make_bibtex_file(bib_dir):
    entry_dirs = list_entry_dirs(bib_dir)

    entries = []
    for entry_dir in entry_dirs:
        try:
            entry = Bibtex.read_bib_entries(
                os.path.join(entry_dir, "reference.bib")
            )[0]
            entries.append(entry)
        except Exception as err:
            print(err)

    bib = {
        "strings": [],
        "preambles": [],
        "entries": entries,
    }

    return minimal_bibtex_io.dumps(bib)
