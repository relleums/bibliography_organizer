Organize your local bibliography
================================
|BlackStyle|

Helps you to organize your local bibliography.


Commands
--------
A set of command-line-tools help you to manage your library. The interface is similar to ``git``.

status
~~~~~~

.. code::
    
    bib status

Prints a list of errors and warnings when your entries are not structrured as expected, or when entries are missing crucial parts.


update
~~~~~~

.. code::

    bib update
    
Tries to update the optical-character-recognition ``ocr``, the ``icon.jpg`` in each entry. Finally updates the search-index in your bibliography directory.
When new originals were added, they are read and added to the ``ocr``. Likewise ``ocr``-records will be ignored when the corresponding original does not longer exist.
The ``icon.jpg`` is extracted from the primary original.

search
~~~~~~

.. code::

    bib search PHRASE
    
Searches for your search-PHRASE in the search-index. Results are printed to the command-line. The search-PHRASE may contain logical operators such as AND, OR, NOT, ANDNOT, and ANDMAYBE.


Structure
---------

The ``bibliography_organizer`` (``biborg``) acts in the ``bibliography_directory``  (``bib_dir``).
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
    |-- citekey_B
    |   |-- original
    |   |   |-- citekey_B.html
    |   |
    |   |-- reference.bib
    |
    |-- .bibliography_organizer
        |-- full_text_search_index

``citekey``
~~~~~~~~~~~
The ``citekey`` is a short string to identify your reference. In your LaTex document you use ``\cite{citekey}``.

Bibliography (``bib_dir``)
~~~~~~~~~~~~~~~~~~~~~~~~~~
The base directory of your local bibliography. It contains your entries and self generated caches such as the search-index.

Entry (``entry_dir``)
~~~~~~~~~~~~~~~~~~~~~
An entry is directory inside the ``bib_dir``. An ``entry_dir`` has the name of the ``citekey``. The ``entry_dir`` contains the original files and a bibtex reference.


To use optical character recognition
------------------------------------

.. code::

    sudo apt-get install tesseract-ocr
    sudo apt-get install imagemagig


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
