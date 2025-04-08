import minimal_bibtex_io
import os
import copy
import re as regular_expression
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


ENTRY_FMT = {}
ENTRY_FMT["author"] = {
    "max_num_authors": 5,
    "abbreviate_secondary_names": True,
}


def make_bib_file(bib_dir, entry_dirs=None, fmt=None, citekey_alias=False):
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
            if len(bib["entries"]) > 0:
                for preamble in bib["preambles"]:
                    out["preamble"].append(preamble)
                for string in bib["strings"]:
                    out["strings"].append(string)

                entry =  bib["entries"][0]
                if fmt:
                    entry["fields"]["author"] = format_author_field(
                        author_field=entry["fields"]["author"], **fmt["author"]
                    )
                out["entries"].append(entry)

                if citekey_alias:
                    citekey_alias_path = os.path.join(entry_dir, "citekey_alias.txt")
                    if os.path.exists(citekey_alias_path):
                        with open(citekey_alias_path, "rt") as f:
                            citekeys = f.read().splitlines()
                        for citekey in citekeys:
                            if fmt:
                                entry["fields"]["author"] = format_author_field(
                                    author_field=entry["fields"]["author"], **fmt["author"]
                                )
                            alias_entry = copy.copy(entry)
                            alias_entry["citekey"] = citekey
                            out["entries"].append(alias_entry)

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


def tokenize_author_field(author_field):
    authors = regular_expression.split(
        " and ", author_field, flags=regular_expression.IGNORECASE
    )
    names = []
    for author in authors:
        nametokens = str.split(author, ",")
        nametokens = [str.strip(token) for token in nametokens]
        names.append(nametokens)
    return names


def format_author_field(
    author_field, max_num_authors, abbreviate_secondary_names
):
    names = tokenize_author_field(author_field)
    and_others = "others" in names[-1]

    num_inames = len(names) - and_others
    num_onames = min([max_num_authors, num_inames])

    if num_onames < num_inames:
        and_others = True

    onames = []
    for i in range(num_onames):
        iname = names[i]
        oname = []
        for j in range(len(iname)):
            if j == 0:
                oname.append(iname[j])
            else:
                secondary = iname[j]
                secondary.strip("{")
                secondary.strip("}")
                oname.append(secondary[0])
        onames.append(oname)

    if and_others:
        onames.append(["others"])

    out = []
    for oname in onames:
        onamestr = str.join(", ", oname)
        out.append(onamestr)

    return str.join(" and ", out)
