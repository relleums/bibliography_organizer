import os
import glob
from . import Status
from . import Bibtex
from . import Entry


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


def update_entries(bib_dir, overwrite_existing_output=False):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        Entry.make_optical_character_recognition(
            entry_dir=entry_dir,
            overwrite_existing_output=overwrite_existing_output,
        )


def update_icons(bib_dir, overwrite_existing_output=False):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        Entry.make_icon(
            entry_dir=entry_dir,
            overwrite_existing_output=overwrite_existing_output,
        )


def update_search_index(bib_dir):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        ocrs = glob.glob(os.path.join(entry_dir, "ocr", "*.tar"))
        if ocrs:
            citekey = os.path.basename(entry_dir)
            Index.add_entry(bib_dir=bib_dir, citekey=citekey)
