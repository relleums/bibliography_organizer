"""
Organize your bibliography
"""
import minimal_bibtex_io
import glob
import os
from . import optical_reader
from . import search_index


def read_bib_entries(path):
    with open(path, "rb") as f:
        raw_bib = minimal_bibtex_io.loads(f.read())
        bib = minimal_bibtex_io.normalize(raw_bib)
    return bib["entries"]


def citekey_list_errors(citekey):
    e = []
    if len(citekey) == 0:
        e.append("E100:Citekey is empty.")

    for char in citekey:
        if str.isupper(char):
            e.append("E101:Citekey has upper case.")
            break

    for char in citekey:
        if str.isspace(char):
            e.append("E102:Citekey has whitespaces.")
            break

    if str.find(citekey, "/") != -1:
        e.append("E103:Citekey has directory seperator '/'.")

    return e


def entry_list_errors(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    opj = os.path.join
    e = []
    if not os.path.isdir(entry_dir):
        e.append("E001:Entry is not a directory.")

    citekey = os.path.basename(entry_dir)
    e += citekey_list_errors(citekey=citekey)

    if os.path.exists(opj(entry_dir, "reference.bib")):
        try:
            bib_entries = read_bib_entries(
                path=opj(entry_dir, "reference.bib")
            )

            if len(bib_entries) > 1:
                e.append("E203:File 'reference.bib' has more than one entry.")

            bib_entry = bib_entries[0]

            if bib_entry["citekey"] != citekey:
                e.append("E204:File 'reference.bib' has different citekey.")

        except Exception as err:
            e.append("E202:File 'reference.bib' is invalid.")
    else:
        e.append("E201:Entry has no 'reference.bib' file.")

    if os.path.isdir(opj(entry_dir, "original")):
        original_paths = _entry_get_original_paths(entry_dir)
        if len(original_paths):
            orig_basenames = [os.path.basename(p) for p in original_paths]
            orig_basenames = [os.path.splitext(p)[0] for p in orig_basenames]

            if not citekey in orig_basenames:
                e.append("W303:No original file with name of citekey.")

            if os.path.exists(opj(entry_dir, "icon.jpg")):
                if os.stat(opj(entry_dir, "icon.jpg")).st_size > 100e3:
                    e.append("W402:Size of 'icon.jpg' > 100kB.")
            else:
                e.append("W401:Entry has no 'icon.jpg'.")

            if os.path.exists(opj(entry_dir, "ocr")):
                ocrs = glob.glob(opj(entry_dir, "ocr", "*"))
                if not len(ocrs):
                    e.append("W502:'ocr' directory is empty.")
            else:
                e.append("W501:Entry has no 'ocr' directory.")

        else:
            e.append("E302:Entry has no files in 'original' directory.")
    else:
        e.append("E301:Entry has no 'original' directory.")

    return e


def _bib_get_entry_dirs(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    entry_dirs = glob.glob(os.path.join(bib_dir, "*"))
    entry_dirs.sort()
    return entry_dirs


def _entry_get_original_paths(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    original_file_paths = glob.glob(os.path.join(entry_dir, "original", "*"))
    original_file_paths.sort()
    return original_file_paths


def _entry_get_primary_original_path(entry_dir):
    citekey = os.path.basename(entry_dir)
    entry_dir = os.path.normpath(entry_dir)
    paths = glob.glob(os.path.join(entry_dir, "original", citekey + "*"))
    paths.sort()
    if paths:
        return paths[0]
    else:
        return None


PRINTABLE = ["jpg", "jpeg", "ps", "pdf", "png", "ppm"]


def _is_printable(path):
    ext = os.path.splitext(path)[1]
    ext = str.lower(ext)
    ext = str.replace(ext, ".", "")
    return ext in PRINTABLE


def bib_print_status(bib_dir):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)

    if len(entry_dirs):
        for entry_dir in entry_dirs:
            errors = entry_list_errors(entry_dir=entry_dir)

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


def bib_make_bibtex_file(bib_dir):
    entry_dirs = _bib_get_entry_dirs(bib_dir)

    entries = []
    for entry_dir in entry_dirs:
        try:
            entry = read_bib_entries(os.path.join(entry_dir, "reference.bib"))[
                0
            ]
            entries.append(entry)
        except Exception as err:
            print(err)

    bib = {
        "strings": [],
        "preambles": [],
        "entries": entries,
    }

    return minimal_bibtex_io.dumps(bib)


def entry_make_ocr(entry_dir, overwrite_existing_output=False):
    original_paths = _entry_get_original_paths(entry_dir)

    if len(original_paths):
        os.makedirs(os.path.join(entry_dir, "ocr"), exist_ok=True)
        basenames_ext = [os.path.basename(p) for p in original_paths]

        for i in range(len(original_paths)):
            document_path = os.path.join(
                entry_dir, "original", basenames_ext[i]
            )
            out_path = os.path.join(
                entry_dir, "ocr", basenames_ext[i] + ".tar"
            )
            if os.path.exists(out_path) and not overwrite_existing_output:
                print("Already done  : ", basenames_ext[i])
            else:
                print("Read original : ", basenames_ext[i])
                try:
                    optical_reader.document_to_string_archive(
                        document_path=document_path, out_path=out_path,
                    )
                except Exception as err:
                    print(err)
    else:
        print("No original   : ", os.path.basename(entry_dir))


def bib_make_ocr(bib_dir, overwrite_existing_output=False):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        entry_make_ocr(
            entry_dir=entry_dir,
            overwrite_existing_output=overwrite_existing_output,
        )


def entry_make_icon(entry_dir, overwrite_existing_output=False):
    citekey = os.path.basename(entry_dir)
    original_paths = _entry_get_original_paths(entry_dir)
    if len(original_paths) > 0:

        primary_path = _entry_get_primary_original_path(entry_dir=entry_dir)
        document_path = primary_path if primary_path else original_paths[0]

        icon_path = os.path.join(entry_dir, "icon.jpg")
        if not os.path.exists(icon_path) or overwrite_existing_output:
            print(citekey, ", Create icon.")
            optical_reader.extract_icon_from_document(
                document_path=document_path,
                out_path=icon_path,
                out_size=100.0e3,
            )
        else:
            print(citekey, ", Skip. Already done.")
    else:
        print(citekey, ", No originals.")


def bib_make_icons(bib_dir, overwrite_existing_output=False):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        entry_make_icon(
            entry_dir=entry_dir,
            overwrite_existing_output=overwrite_existing_output,
        )


def bib_update_search_index(bib_dir):
    entry_dirs = _bib_get_entry_dirs(bib_dir=bib_dir)
    for entry_dir in entry_dirs:
        ocrs = glob.glob(os.path.join(entry_dir, "ocr", "*.tar"))
        if ocrs:
            citekey = os.path.basename(entry_dir)
            print(citekey)
            search_index.add_entry(bib_dir=bib_dir, citekey=citekey)
