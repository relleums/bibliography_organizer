import setuptools

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="bibliography_organizer",
    version="1.1.2",
    description="Organize your bibliography",
    long_description=long_description,
    url="https://github.com/relleums",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    license="MIT",
    packages=["bibliography_organizer", "bibliography_organizer.scripts"],
    install_requires=["minimal_bibtex_io", "pytesseract", "whoosh"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
    ],
    entry_points={
        "console_scripts": ["bib=bibliography_organizer.scripts.main:main",]
    },
    python_requires=">=3",
)
