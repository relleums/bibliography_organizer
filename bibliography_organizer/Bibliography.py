import os
import glob
from . import Status
from . import Bibtex


def list_entry_dirs(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    entry_dirs = glob.glob(os.path.join(bib_dir, "*"))
    entry_dirs.sort()
    return entry_dirs


def print_status(bib_dir):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)

    if len(entry_dirs):
        for entry_dir in entry_dirs:
            errors = Status.list_errors_in_entry(entry_dir=entry_dir)

            citekey = os.path.basename(entry_dir)
            for msg in errors:
                err_code_str = msg[0:4]
                err_msg = msg[5:]
                print(
                    "{:40s} {:s} {:s}".format(citekey, err_code_str, err_msg)
                )
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


def bib_update_search_index(bib_dir):
    entry_dirs = list_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        ocrs = glob.glob(os.path.join(entry_dir, "ocr", "*.tar"))
        if ocrs:
            citekey = os.path.basename(entry_dir)
            print(citekey)
            search_index.add_entry(bib_dir=bib_dir, citekey=citekey)
