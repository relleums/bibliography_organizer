import os
import tempfile
import subprocess
import shutil


def extract_icon(document_path, out_path, out_size=100.0e3):
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
                "-strip",
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


def convert_to_images(document_path, out_dir, image_format="jpg"):
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
