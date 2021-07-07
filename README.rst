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
    |-- citekey_A  <--entry_dir created by user.
    |   |-- original
    |   |   |-- citekey_A.pdf
    |   |   |-- comments.ps
    |   |   |-- preprint.pdf
    |   |
    |   |-- reference.bib
    |
    |-- citekey_B  <--entry_dir created by user.
    |   |-- original
    |   |   |-- citekey_B.html
    |   |
    |   |-- reference.bib
    |
    |-- .bibliography_organizer  <--creted automatically.
        |-- full_text_search_index

``citekey``
~~~~~~~~~~~
The ``citekey`` is a short string to identify your reference. In LaTex you use ``\cite{citekey}``.

``bib_dir``
~~~~~~~~~~~
The base directory of your local bibliography. Here, you create and collect your entries in ``entry_dir``s.  ``biborg`` will create a hidden cache in here named ``.bibliography_organizer``.

``entry_dir``
~~~~~~~~~~~~~
An ``entry_dir`` is directory inside your ``bib_dir``. An ``entry_dir`` has the name of the ``citekey``. The ``entry_dir`` contains the original files and a bibtex reference. You create, and populate the ``entry_dir``s in your ``bib_dir``.

``original``
~~~~~~~~~~~~
In every ``entry_dir`` is the original directory. It contains the original files to be cited. Usually, there is only one original-file corresponding to one ``citekey``. But sometimes the original might be a collection of files like a web-page or such. The user creates the original directory and populates it with her originals.


To use optical character recognition
------------------------------------

.. code::

    sudo apt-get install tesseract-ocr
    sudo apt-get install imagemagig


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
