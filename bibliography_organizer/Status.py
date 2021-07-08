import os
import glob
from . import Entry
from . import Bibtex


def _has_upper_char(text):
    for char in text:
        if str.isupper(char):
            return True
    return False


def _has_space_char(text):
    for char in text:
        if str.isspace(char):
            return True
    return False


def list_errors_in_citekey(citekey):
    e = []
    if len(citekey) == 0:
        e.append("E100:Citekey is empty.")

    if _has_upper_char(citekey):
        e.append("E101:Citekey has upper case.")

    if _has_space_char(citekey):
        e.append("E102:Citekey has whitespaces.")

    if str.find(citekey, "/") != -1:
        e.append("E103:Citekey has directory seperator '/'.")

    return e


def list_errors_in_bibtex_entry(bib_entry):
    e = []

    for key in bib_entry["fields"]:
        if len(key) == 0:
            e.append("E220:Bibtex fieldkey is empty.")

        if _has_upper_char(key):
            e.append("E221:Bibtex fieldkey '{:s}' has upper case.".format(key))

        if _has_space_char(key):
            e.append("E222:Bibtex fieldkey '{:s}' has whitespace.".format(key))

        if str.find(key, "/") != -1:
            e.append("E223:Bibtex fieldkey '{:s}' has seperator.".format(key))

    if "title" not in bib_entry["fields"]:
        e.append("E230:Bibtex has no 'title' field.")

    if "author" not in bib_entry["fields"]:
        e.append("E231:Bibtex has no 'author' field.")

    for key in bib_entry["fields"]:
        value = bib_entry["fields"][key]
        if Bibtex.is_wrapped_in_braces(value):
            e.append(
                "W240:Bibtex value of field '{:s}' "
                "is wrapped in braces '{{}}'.".format(key)
            )
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
            bib = Bibtex.read(path=opj(entry_dir, "reference.bib"))

            if len(bib["entries"]) > 1:
                e.append("E203:File 'reference.bib' has more than one entry.")

            bib_entry = bib["entries"][0]
            if bib_entry["citekey"] != citekey:
                e.append("E204:File 'reference.bib' has different citekey.")
            e += list_errors_in_bibtex_entry(bib_entry=bib_entry)

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
                e.append("E303:No original file with name of citekey.")

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
