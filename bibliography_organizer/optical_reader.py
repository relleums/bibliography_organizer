import pytesseract
import os
import tempfile
import subprocess
import glob
import tarfile
import io
import shutil
import PIL


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
    os.makedirs(out_dir, exist_ok=True)
    call = [
        "convert",
        "-density",
        "400",
        "-alpha",
        "remove",
        "-quality",
        "92",
        document_path,
        os.path.join(out_dir, "%06d." + image_format),
    ]
    subprocess.call(call)


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
