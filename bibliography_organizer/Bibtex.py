import minimal_bibtex_io
import os
from . import Bibliography


def read_raw(path):
    with open(path, "rb") as f:
        raw_bib = minimal_bibtex_io.loads(f.read())
    return raw_bib


def normalize(raw_bib):
    return minimal_bibtex_io.normalize(raw_bib)


def read(path):
    raw_bib = read_raw(path)
    return normalize(raw_bib)


def make_bib_file(bib_dir, entry_dirs=None):
    if entry_dirs is None:
        entry_dirs = Bibliography.list_entry_dirs(bib_dir)

    out = {
        "strings": [],
        "preambles": [],
        "entries": [],
    }
    for entry_dir in entry_dirs:
        try:
            bib = read(os.path.join(entry_dir, "reference.bib"))
            for preamble in bib["preambles"]:
                out["preamble"].append(preamble)
            for string in bib["strings"]:
                out["strings"].append(string)
            for entry in bib["entries"]:
                out["entries"].append(entry)
        except Exception as err:
            print(err)
    return minimal_bibtex_io.dumps(out)


def is_wrapped_in_braces(text):
    B = bytes(text, encoding="utf8")
    start, stop = minimal_bibtex_io._find_braces_start_stop(B=B)
    if start == 0 and stop == len(B) - 1:
        return True
    else:
        return False
