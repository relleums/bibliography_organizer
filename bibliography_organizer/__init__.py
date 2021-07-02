"""
Organize your bibliography
"""
import minimal_bibtex_io
import glob
import os
from . import optical_reader


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

    st["original_dir_exists"] = os.path.isdir(
        os.path.join(entry_dir, "original")
    )
    st["original_files"] = glob.glob(os.path.join(entry_dir, "original", "*"))
    if st["original_files"]:
        st["original_files_exist"] = True
    else:
        st["original_files_exist"] = False

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


def _bib_get_entry_dirs(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    entry_dirs = glob.glob(os.path.join(bib_dir, "*"))
    entry_dirs.sort()
    return entry_dirs


PRINTABLE = ["jpg", "jpeg", "ps", "pdf", "png", "ppm"]


def _is_printable(path):
    ext = os.path.splitext(path)[1]
    ext = str.lower(ext)
    ext = str.replace(ext, ".", "")
    return ext in PRINTABLE


def _entry_get_original_paths(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    original_file_paths = glob.glob(os.path.join(entry_dir, "original", "*"))
    original_file_paths.sort()
    return original_file_paths


def bib_print_status(bib_dir):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)

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

        if not status["original_dir_exists"]:
            print(_ERR(ck, "has no original-dir"))
        else:
            if not status["original_files_exist"]:
                print(_ERR(ck, "has no originals"))

        if not status["reference_bib_exists"]:
            print(_ERR(ck, "has no reference.bib"))
        else:
            if not status["reference_bib_valid"]:
                print(_ERR(ck, "reference.bib' is not valid"))

            if not status["equal_citekey_in_basename_and_bib"]:
                print(_ERR(ck, "citekey mismatch"))


def bib_make_bibtex_file(bib_dir):
    entry_dirs = _bib_get_entry_dirs(bib_dir)

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


def bib_read_originals_to_txt(bib_dir, overwrite_existing_output=False):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)

    for entry_dir in entry_dirs:
        entry_status = entry_estimate_status(entry_dir)

        if entry_status["original_files_exist"]:
            os.makedirs(os.path.join(entry_dir, "ocr"), exist_ok=True)

            original_file_paths = _entry_get_original_paths(entry_dir)
            basenames_ext = [os.path.basename(p) for p in original_file_paths]
            basenames = [os.path.splitext(b)[0] for b in basenames_ext]

            for i in range(len(original_file_paths)):
                document_path = os.path.join(
                    entry_dir, "original", basenames_ext[i]
                )
                out_path = os.path.join(
                    entry_dir, "ocr", basenames[i] + ".tar"
                )
                if os.path.exists(out_path) and not overwrite_existing_output:
                    print("Already done  : ", basenames[i])
                else:
                    print("Read original : ", basenames[i])
                    try:
                        optical_reader.document_to_string_archive(
                            document_path=document_path, out_path=out_path,
                        )
                    except Exception as err:
                        print(err)
        else:
            print("No original   : ", os.path.basename(entry_dir))


def bib_make_icons(bib_dir, overwrite_existing_output=False):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)

    for entry_dir in entry_dirs:
        citekey = os.path.basename(entry_dir)
        original_file_paths = _entry_get_original_paths(entry_dir)
        original_file_paths = [
            p for p in original_file_paths if _is_printable(p)
        ]
        if len(original_file_paths) > 0:
            icon_path = os.path.join(entry_dir, "icon.jpg")

            if not os.path.exists(icon_path) or overwrite_existing_output:
                print(citekey, ", Create icon.")
                optical_reader.extract_icon_from_document(
                    document_path=original_file_paths[0],
                    out_path=icon_path,
                    out_size=100.0e3,
                )
            else:
                print(citekey, ", Skip. Already done.")
        else:
            print(citekey, ", No originals.")
