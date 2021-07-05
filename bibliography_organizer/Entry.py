import os
import glob
import textwrap
from . import Document
from . import Reader
from . import Status
from . import Bibtex



def list_original_paths(entry_dir):
    """
    Returns a list of original documnet paths.
    Document-file-names equal to the citekey go first in the list.
    """
    entry_dir = os.path.normpath(entry_dir)
    citekey = os.path.basename(entry_dir)
    original_paths = glob.glob(os.path.join(entry_dir, "original", "*"))
    primary_paths = glob.glob(
        os.path.join(entry_dir, "original", citekey + "*")
    )
    original_paths.sort()
    primary_paths.sort()
    out = []
    for prim in primary_paths:
        out.append(prim)
    for orig in original_paths:
        if orig not in out:
            out.append(orig)
    return out


def vprint(verbose, *args):
    if verbose:
        print(*args)


def make_icon(entry_dir, overwrite=False, verbose=False):
    entry_dir = os.path.normpath(entry_dir)
    citekey = os.path.basename(entry_dir)
    original_paths = list_original_paths(entry_dir)

    if len(original_paths) > 0:
        icon_path = os.path.join(entry_dir, "icon.jpg")
        if not os.path.exists(icon_path) or overwrite:
            print(citekey, ", Create icon.")
            Document.extract_icon(
                document_path=original_paths[0],
                out_path=icon_path,
                out_size=100.0e3,
            )
        else:
            vprint(verbose, citekey, ", Skip. Already done.")
    else:
        vprint(verbose, citekey, ", No originals.")


def make_optical_character_recognition(entry_dir, overwrite=False, verbose=False):
    entry_dir = os.path.normpath(entry_dir)
    citekey = os.path.basename(entry_dir)
    original_paths = list_original_paths(entry_dir)

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
            if os.path.exists(out_path) and not overwrite:
                vprint(verbose, citekey, ", Already done", basenames_ext[i])
            else:
                print(citekey, ", Read", basenames_ext[i])
                try:
                    Reader.document_to_string_archive(
                        document_path=document_path, out_path=out_path,
                    )
                except Exception as err:
                    print(err)
    else:
        vprint(verbose, citekey, ", No originals")


def update(entry_dir, overwrite=False):
    make_icon(entry_dir, overwrite)
    make_optical_character_recognition(entry_dir, overwrite)


def print_status(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    errors = Status.list_errors_in_entry(entry_dir=entry_dir)
    citekey = os.path.basename(entry_dir)
    for msg in errors:
        err_code_str = msg[0:4]
        err_msg = msg[5:]
        print(
            "{:40s} {:s} {:s}".format(citekey, err_code_str, err_msg)
        )


def _print_field(field, width, indent, num_lines=-1):
    out = ""
    out += " "*indent
    lines = textwrap.wrap(Bibtex.normalize(field), width=width)
    if num_lines > 0:
        lines = lines[0:num_lines]
    out += ("\n" + " "*indent).join(lines) +'\n'
    return out


def print_overview(
    entry_dir,
    width=79,
    indent=4,
    original_filename=None,
    num_filed_lines=1
):
    citekey = os.path.basename(entry_dir)

    out = citekey
    if original_filename:
        out += " : " + original_filename
    out += "\n"
    out += "-"*len(citekey) + "\n"

    bib_file_path = os.path.join(entry_dir, "reference.bib")
    if os.path.exists(bib_file_path):
        bib = Bibtex.read_bib_entries(path=bib_file_path)[0]
        fields = bib["fields"]

        for key in ["title", "author", "year"]:
            if key in fields:
                out += _print_field(
                    fields[key],
                    width=width,
                    indent=indent,
                    num_lines=num_filed_lines
                )
    print(out)