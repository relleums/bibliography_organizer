import minimal_bibtex_io


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