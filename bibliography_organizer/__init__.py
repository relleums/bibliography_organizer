"""
Organize your bibliography
"""
import minimal_bibtex_io
import glob
import os


def read_bib_entry(path):
    with open(path, "rb") as f:
        raw_bib = minimal_bibtex_io.loads(f.read())
        bib = minimal_bibtex_io.normalize(raw_bib)
    return bib["entries"][0]


def citekey_estimate_status(citekey):
    status = {}
    status["is_all_lowercase"] = True
    status["is_all_blackspace"] = True
    for char in citekey:
        if str.isupper(char):
            status["is_all_lowercase"] = False
            break
        if str.isspace(char):
            status["is_all_blackspace"] = False
            break

    return status


def entry_estimate_status(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    st = {}

    st["originals_dir_exists"] = os.path.isdir(
        os.path.join(entry_dir, "original")
    )
    st["originals_files"] = glob.glob(
        os.path.join(entry_dir, "original", "*")
    )
    if st["originals_files"]:
        st["originals_files_exist"] = True
    else:
        st["originals_files_exist"] = False

    reference_bib_path = os.path.join(entry_dir, "reference.bib")
    st["reference_bib_exists"] = os.path.exists(reference_bib_path)
    try:
        entry = read_bib_entry(path=reference_bib_path)
        st["reference_bib_valid"] = True
    except Exception as exc:
        st["reference_bib_valid"] = False

    if st["reference_bib_valid"]:
        entry_dir_citekey = os.path.basename(entry_dir)
        entry_citekey = entry["citekey"]
        st["equal_citekey_in_basename_and_bib"] = (
            entry_dir_citekey == entry_citekey
        )
    else:
        st["equal_citekey_in_basename_and_bib"] = False
    return st


ERRORS = {
    "is not a directory": 1,
    "has no original-dir": 101,
    "has no originals": 102,
    "citekey has uppercase": 11,
    "citekey mismatch": 20,
    "has no reference.bib": 200,
    "reference.bib' is not valid": 201,
}


def _ERR(citekey, msg):
    quoted_citekey = '"' + citekey + '"'
    if msg in ERRORS:
        error_str = "E{:03d}".format(ERRORS[msg])
    else:
        error_str = "E???"
    return "{error_str:s}: {citekey:40s} {msg:s}.".format(
        error_str=error_str, citekey=quoted_citekey, msg=msg
    )


def _get_entry_dirs(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    return glob.glob(os.path.join(bib_dir, "*"))


def bib_print_status(bib_dir):
    entry_dirs = _get_entry_dirs(bib_dir)

    if len(entry_dirs) == 0:
        print("No bibliography entries in '{:s}'".format(bib_dir))
        print("Maybe thit is not a bibliography directory?")

    for entry_dir in entry_dirs:
        ck = os.path.basename(entry_dir)

        citekey_status = citekey_estimate_status(ck)

        if not os.path.isdir(entry_dir):
            print(_ERR(ck, "is not a directory"))
            continue

        if not citekey_status["is_all_lowercase"]:
            print(_ERR(ck, "citekey has uppercase"))

        if not citekey_status["is_all_blackspace"]:
            print(_ERR(ck, "citekey has spaces"))

        status = entry_estimate_status(entry_dir)

        if not status["originals_dir_exists"]:
            print(_ERR(ck, "has no original-dir"))
        else:
            if not status["originals_files_exist"]:
                print(_ERR(ck, "has no originals"))

        if not status["reference_bib_exists"]:
            print(_ERR(ck, "has no reference.bib"))
        else:
            if not status["reference_bib_valid"]:
                print(_ERR(ck, "reference.bib' is not valid"))

            if not status["equal_citekey_in_basename_and_bib"]:
                print(_ERR(ck, "citekey mismatch"))


def bib_make_bibtex_file(bib_dir):
    entry_dirs = _get_entry_dirs(bib_dir)

    entries = []
    for entry_dir in entry_dirs:
        try:
            entry = read_bib_entry(os.path.join(entry_dir, "reference.bib"))
            entries.append(entry)
        except Exception as err:
            print(err)

    bib = {
        "strings": [],
        "preambles": [],
        "entries": entries,
    }

    return minimal_bibtex_io.dumps(bib)
