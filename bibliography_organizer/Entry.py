import os
import glob
import textwrap
import shutil
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


def make_icon(entry_dir, verbose=False):
    entry_dir = os.path.normpath(entry_dir)
    citekey = os.path.basename(entry_dir)
    original_paths = list_original_paths(entry_dir)

    if len(original_paths) > 0:
        icon_path = os.path.join(entry_dir, "icon.jpg")
        if not os.path.exists(icon_path):
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


def list_ocr_paths(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    arcs = []
    orc_wildcard = os.path.join(entry_dir, "ocr", "*.tar")
    for archive_path in glob.glob(orc_wildcard):
        arcs.append(archive_path)
    return arcs


def hide_file_in_its_directory(path):
    path = os.path.normpath(path)
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    shutil.move(
        src=os.path.join(dirname, basename),
        dst=os.path.join(dirname, "." + basename),
    )


def update_optical_character_recognition(entry_dir, verbose=False):
    entry_dir = os.path.normpath(entry_dir)
    citekey = os.path.basename(entry_dir)
    os.makedirs(os.path.join(entry_dir, "ocr"), exist_ok=True)

    original_paths = list_original_paths(entry_dir)
    ocr_paths = list_ocr_paths(entry_dir)

    for ocr_path in ocr_paths:
        ocr_original_filename = os.path.splitext(os.path.basename(ocr_path))[0]
        ocr_original_path = os.path.join(
            entry_dir, "original", ocr_original_filename
        )

        if not os.path.exists(ocr_original_path):
            vprint(
                verbose,
                "{:s} : No original for OCR {:s}. Ignore OCR.".format(
                    citekey, ocr_original_filename
                ),
            )
            hide_file_in_its_directory(ocr_path)

    for original_path in original_paths:
        original_filename = os.path.basename(original_path)
        orig_ocr_path = os.path.join(
            entry_dir, "ocr", original_filename + ".tar"
        )
        if orig_ocr_path not in ocr_paths:
            vprint(
                verbose,
                "{:s} : New original {:s}. Create OCR.".format(
                    citekey, original_filename
                ),
            )
            try:
                Reader.document_to_string_archive(
                    document_path=original_path, out_path=orig_ocr_path,
                )
            except Exception as err:
                print(err)


def print_status(entry_dir):
    entry_dir = os.path.normpath(entry_dir)
    errors = Status.list_errors_in_entry(entry_dir=entry_dir)
    citekey = os.path.basename(entry_dir)
    for msg in errors:
        err_code_str = msg[0:4]
        err_msg = msg[5:]
        print("{:40s} {:s} {:s}".format(citekey, err_code_str, err_msg))


def _print_field(field, width, indent, num_lines=-1):
    out = ""
    out += " " * indent
    lines = textwrap.wrap(field, width=width)
    if num_lines > 0:
        lines = lines[0:num_lines]
    out += ("\n" + " " * indent).join(lines) + "\n"
    return out


def print_overview(
    entry_dir, width=79, indent=4, original_filename=None, num_filed_lines=1
):
    citekey = os.path.basename(entry_dir)

    out = citekey
    if original_filename:
        out += " : " + original_filename
    out += "\n"
    out += "-" * len(citekey) + "\n"

    bib_file_path = os.path.join(entry_dir, "reference.bib")
    if os.path.exists(bib_file_path):
        bib = Bibtex.read(path=bib_file_path)
        bib_entry = bib["entries"][0]
        fields = bib_entry["fields"]

        for key in ["title", "author", "year"]:
            if key in fields:
                out += _print_field(
                    fields[key],
                    width=width,
                    indent=indent,
                    num_lines=num_filed_lines,
                )
    print(out)
