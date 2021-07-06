import minimal_bibtex_io
import os
from . import Bibliography

def read_bib_entries(path):
    """
    Reads a bibtex-file and parses only the entries.
    I.e. it ignores '@string' and '@preamble' entries.
    """
    with open(path, "rb") as f:
        raw_bib = minimal_bibtex_io.loads(f.read())
        bib = minimal_bibtex_io.normalize(raw_bib)

    if bib["strings"] or bib["preambles"]:
        print("WARNING: Ignoring @string and @preamble in {:s}".format(path))

    return bib["entries"]


def normalize(text):
    raw = str(text)
    raw = raw.replace("{", "")
    raw = raw.replace("}", "")
    raw = " ".join(raw.split())
    return raw


def make_bib_file(bib_dir, entry_dirs=None):
    if entry_dirs is None:
        entry_dirs = Bibliography.list_entry_dirs(bib_dir)

    entries = []
    for entry_dir in entry_dirs:
        try:
            entry = read_bib_entries(
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
