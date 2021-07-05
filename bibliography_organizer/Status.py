import os
import glob
from . import Entry
from . import Bibtex


def list_errors_in_citekey(citekey):
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


def list_errors_in_entry(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    opj = os.path.join
    e = []
    if not os.path.isdir(entry_dir):
        e.append("E001:Entry is not a directory.")

    citekey = os.path.basename(entry_dir)
    e += list_errors_in_citekey(citekey=citekey)

    if os.path.exists(opj(entry_dir, "reference.bib")):
        try:
            bib_entries = Bibtex.read_bib_entries(
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
        original_paths = Entry.list_original_paths(entry_dir)
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
