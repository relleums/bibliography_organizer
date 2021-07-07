Bibliography Organizer
======================
|BlackStyle|

Helps you to organize and search your local bibliography. ``biborg`` is not invasive, it does not touch your cited documents or bibtex-files. ``biborg`` only offers suggestions to organize your files, as well as a full-text-search.
``biborg`` acts in the filesystem. Its interface is motivated by the version-control-tool ``git``.

Commands
--------
A set of command-line-tools to help you managing your bibliography. The interface is similar to ``git``.

``bib status``
~~~~~~~~~~~~~~
Prints a list of errors and warnings when your entries are not structrured as expected, or when entries are missing crucial parts.

``bib update``
~~~~~~~~~~~~~~
Tries to update the optical-character-recognition ``ocr``, the ``icon.jpg`` in each entry. Finally updates the search-index in your bibliography directory.
When new originals were added, they are read and added to the ``ocr``. Likewise ``ocr``-records will be ignored when the corresponding original does not longer exist.
The ``icon.jpg`` is extracted from the primary original.

``bib search``
~~~~~~~~~~~~~~
Searches for your search-``PHRASE`` in the search-index. Results are printed to the command-line. The search-``PHRASE`` may contain logical operators such as ``AND``, ``OR``, ``NOT``, ``ANDNOT``, ``ANDMAYBE``, ``(``, and ``)``. See documnetation of ``Whoosh``.


Structure
---------

The ``bibliography_organizer``, or ``biborg`` for short, acts in your bibliography directory ``bib_dir``.
The ``bib_dir`` can be any directory in your filesystem. ``biborg``'s command-line-interface expects the current working directory to be a ``bib_dir``.


.. code::

    bib_dir
    |-- citekey_A
    |   |-- original
    |   |   |-- citekey_A.pdf
    |   |   |-- comments.ps
    |   |   |-- preprint.pdf
    |   |
    |   |-- reference.bib
    |
    |-- citekey_B                       <-- you
    |   |-- original                    <-- you
    |   |   |-- citekey_B.html          <-- you
    |   |
    |   |-- reference.bib               <-- you
    |   | 
    |   |-- ocr                         <-- biborg
    |   |   |-- citekey_B.html.tar      <-- biborg
    |   |
    |   |-- icon.jpg                    <-- biborg
    |
    |-- .bibliography_organizer         <-- biborg
        |-- full_text_search_index

Terminology
-----------

``citekey``
~~~~~~~~~~~
The ``citekey`` is a string to identify your reference, e.g. 'darwin1859origin'. In LaTex you use ``\cite{citekey}``.

``bib_dir``
~~~~~~~~~~~
The base directory of your local bibliography. Here, you create and collect your entries in ``entry_dir``s.  ``biborg`` will create a hidden cache in here named ``.bibliography_organizer``.

``entry_dir``
~~~~~~~~~~~~~
An ``entry_dir`` is directory inside your ``bib_dir``. An ``entry_dir`` has the name of the ``citekey``. The ``entry_dir`` contains the original files and a bibtex reference. You create, and populate the ``entry_dir``s in your ``bib_dir``.

``original``
~~~~~~~~~~~~
In every ``entry_dir`` is the original directory. It contains the original files to be cited. Usually, there is only one original-file corresponding to one ``citekey``. But sometimes the original might be a collection of files like a web-page or such. You create the original directory and populate it with your originals.

``reference.bib``
~~~~~~~~~~~~~~~~~
A bibtex-file in the ``entry_dir`` that you create. It contains exactly one bibtex-entry. The ``citekey`` in the bibtex-entry is expected to match the ``entry_dir``.

``ocr``
~~~~~~~~
The ``ocr`` directory is created and updated by ``biborg``. The ``ocr`` directory contains the extracted text from the original files. The text is extracted using optical character recognition. Each original file has one archive in the ``ocr`` directory. The archive contains the text of the individual pages from the original.
This is used to fill the search-index.

``icon``
~~~~~~~~
The ``icon.jpg`` is a small image rendered from the first page of the primary original-file. The ``icon.jpg`` is created by ``biborg``.
The primary original file has the ``citekey`` as its basename.

``full_text_search_index``
~~~~~~~~~~~~~~~~~~~~~~~~~~
This is a hidden directory in ``bib_dir/.bibliography_organizer/full_text_search_index``. It is a cache for the search created and updated by ``biborg``.

To use optical character recognition
------------------------------------

.. code::

    sudo apt-get install tesseract-ocr
    sudo apt-get install imagemagig


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
