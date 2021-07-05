import pytesseract
import PIL
import io
import tarfile
import shutil
import os
import glob
import tempfile
from . import Document


def parse_image_to_string(image_path):
    with PIL.Image.open(image_path) as img:
        s = pytesseract.image_to_string(img)
    return s


def document_to_string_archive(document_path, out_path):
    out_path = os.path.normpath(out_path)
    out_dirname = os.path.dirname(out_path)
    os.makedirs(out_dirname, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:

        Document.convert_to_images(
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
