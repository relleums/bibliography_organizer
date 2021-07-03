import pytesseract
import os
import tempfile
import subprocess
import glob
import tarfile
import io
import shutil
import PIL
import re
import json


def extract_icon_from_document(document_path, out_path, out_size=100.0e3):
    out_path = os.path.normpath(out_path)
    ext = os.path.splitext(out_path)[1]
    basename = os.path.basename(out_path)

    document_path_first_page = document_path + "[0]"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp0_out_path = os.path.join(tmp_dir, "0-" + basename + "." + ext)
        tmp1_out_path = os.path.join(tmp_dir, "1-" + basename + "." + ext)

        subprocess.call(
            [
                "convert",
                "-density",
                "150",
                "-alpha",
                "remove",
                document_path_first_page,
                tmp0_out_path,
            ]
        )
        quality = 92
        min_icon_size = 128
        icon_size = 512
        while quality > 20:
            subprocess.call(
                [
                    "convert",
                    tmp0_out_path,
                    "-resize",
                    "{:d}x{:d}^".format(icon_size, icon_size),
                    "-gravity",
                    "north",
                    "-extent",
                    "{:d}x{:d}".format(icon_size, icon_size),
                    "-quality",
                    str(quality),
                    tmp1_out_path,
                ]
            ),
            actual_size = os.stat(tmp1_out_path).st_size
            if actual_size <= out_size:
                break
            if icon_size > min_icon_size:
                icon_size -= 8
            else:
                quality -= 2

        shutil.move(src=tmp1_out_path, dst=out_path)


def convert_documnet_to_images(document_path, out_dir, image_format="jpg"):
    pagenumber = 0
    return_code = 0
    while return_code == 0:
        process = subprocess.Popen(
            [
                "convert",
                "-density",
                "200",
                "-alpha",
                "remove",
                "-quality",
                "92",
                document_path + "[{:d}]".format(pagenumber),
                os.path.join(
                    out_dir, "{:06d}.".format(pagenumber) + image_format
                ),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return_code = process.wait()
        stdout, stderr = process.communicate()
        if stderr:
            if bytes.find(stderr, b"FirstPage > LastPage") == -1:
                print(stderr)
        if stdout:
            print(stdout)
        pagenumber += 1


def parse_image_to_string(image_path):
    with PIL.Image.open(image_path) as img:
        s = pytesseract.image_to_string(img)
    return s


def document_to_string_archive(document_path, out_path):
    out_path = os.path.normpath(out_path)
    out_dirname = os.path.dirname(out_path)
    os.makedirs(out_dirname, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:

        convert_documnet_to_images(
            document_path=document_path, out_dir=tmp_dir, image_format="jpg"
        )

        image_paths = glob.glob(os.path.join(tmp_dir, "*.jpg"))
        img_basenames = [os.path.basename(p) for p in image_paths]
        img_basenames.sort()
        image_paths = [os.path.join(tmp_dir, bn) for bn in img_basenames]

        tmp_out_path = os.path.join(tmp_dir, "out.tar")
        with tarfile.open(tmp_out_path, "w") as tarout:
            for image_path in image_paths:
                page_number = 1 + int(os.path.basename(image_path)[0:6])
                page_string = parse_image_to_string(image_path=image_path)

                page_bytes = page_string.encode()
                buff = io.BytesIO()

                info = tarfile.TarInfo()
                info.name = "page_{:06d}.txt".format(page_number)
                info.size = buff.write(page_bytes)

                buff.seek(0)
                tarout.addfile(tarinfo=info, fileobj=buff)
                buff.close()
        shutil.move(src=tmp_out_path, dst=out_path)


def read_string_archive(path):
    arc = {}
    with tarfile.open(path, "r") as tarin:
        for info in tarin:
            assert str.endswith(info.name, ".txt")
            assert str.startswith(info.name, "page_")
            number_str = info.name[5:11]
            page_number = int(number_str)
            buff = tarin.extractfile(info)
            text_b = buff.read()
            text_u = bytes.decode(text_b, encoding="utf-8")
            arc[page_number] = text_u
    return arc


def key_normalizer(key):
    out = str(key)
    out = str.strip(out)
    out = str.lower(out)
    out = re.sub(r"^\W+|\W+$", "", out)
    try:
        _ = float(out)
        if len(out) < 4:
            out = ""
    except Exception as err:
        pass
    if len(out) < 2:
        out = ""
    return out


def normalize_page(page_text):
    out = str(page_text)
    out = str.split(out)
    ll = {}
    for pos, token in enumerate(out):
        ntoken = key_normalizer(token)
        if ntoken:
            if ntoken in ll:
                ll[ntoken].append(pos)
            else:
                ll[ntoken] = [pos]
    return ll


def normalize_archive(arc):
    arc_index = {}
    for pagenumber in arc:
        page_index = normalize_page(page_text=arc[pagenumber])

        for token in page_index:
            if token not in arc_index:
                arc_index[token] = []
            for token_pos in page_index[token]:
                arc_index[token].append((pagenumber, token_pos))
    return arc_index


def archive_to_index(arc, filename):
    ind = {}
    ind["filename/page"] = []
    for pagenumber in arc:
        ind["filename/page"].append(filename + "{:06d}".format(pagenumber))
    ind["index"] = {}
    for pagenumber in arc:
        page_text = arc[pagenumber]
        block = normalize_text_block(text=page_text)
        for token in block:
            if token in ind["index"]:
                ind["index"][token].append(pagenumber)
            else:
                ind["index"][token] = [pagenumber]
    return ind


def serialize_search_index(search_index):
    buff = io.BytesIO()
    for token in search_index:
        buff.write(str.encode(token, encoding="utf8"))
        buff.write(b"\n")
        ref_str = json.dumps(search_index[token], indent=None)
        buff.write(str.encode(ref_str, encoding="utf8"))
        buff.write(b"\n")
    buff.seek(0)
    return buff.read()
