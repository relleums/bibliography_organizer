import whoosh
import whoosh.fields
import whoosh.index
import whoosh.query
import whoosh.qparser
import os
import glob
from . import Reader
from . import Bibliography

INDEX_DIRNAME = "full_text_search_index"


def get_schema():
    return whoosh.fields.Schema(
        path=whoosh.fields.ID(unique=True, stored=True),
        content=whoosh.fields.TEXT(stored=True),
        modtime=whoosh.fields.STORED,
    )


def list_all_docs_in_bibliography(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    entry_dirs = Bibliography.list_entry_dirs(bib_dir=bib_dir)

    docs = []
    for entry_dir in entry_dirs:
        orc_wildcard = os.path.join(entry_dir, "ocr", "*.tar")
        for string_archive_path in glob.glob(orc_wildcard):
            docs.append(string_archive_path)
    return docs


def add_doc(index_writer, path):
    path = os.path.normpath(path)
    citekey, original_filename = _split_path(path)
    print(citekey, "Add to index", original_filename)

    assert os.path.splitext(path)[1] == ".tar"
    arc = Reader.read_string_archive(path=path)

    content = ""
    for pagenumber in arc:
        content += arc[pagenumber] + "\n\n"
    index_writer.add_document(
        content=content,
        path=os.path.join(citekey, "ocr", original_filename + ".tar"),
        modtime=os.path.getmtime(path),
    )


def make_clean_index(bib_dir):
    # Create the index from scratch
    index = whoosh.index.create_in(get_index_dir(bib_dir), schema=get_schema())
    index_writer = index.writer()
    for doc_path in list_all_docs_in_bibliography(bib_dir=bib_dir):
        add_doc(index_writer=index_writer, path=doc_path)
    print("Commit changes to index.")
    index_writer.commit()


def increment_index(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    index = whoosh.index.open_dir(get_index_dir(bib_dir))

    # The set of all paths in the index
    indexed_paths = set()
    # The set of all paths we need to re-index
    to_index = set()

    with index.searcher() as searcher:
        index_writer = index.writer()

        for fields in searcher.all_stored_fields():
            indexed_path = fields["path"]
            citekey, original_filename = _split_path(indexed_path)
            indexed_paths.add(os.path.join(bib_dir, indexed_path))

            if not os.path.exists(indexed_path):
                index_writer.delete_by_term("path", indexed_path)
                print(
                    citekey,
                    original_filename,
                    "Delete from Index.",
                    "This file was deleted since it was indexed",
                )

            else:
                indexed_time = fields["modtime"]
                mtime = os.path.getmtime(indexed_path)
                if mtime > indexed_time:
                    index_writer.delete_by_term("path", indexed_path)
                    to_index.add(os.path.join(bib_dir, indexed_path))
                    print(
                        citekey,
                        original_filename,
                        "The file has changed, delete and reindex",
                    )

    for path in list_all_docs_in_bibliography(bib_dir=bib_dir):
        if path in to_index or path not in indexed_paths:
            citekey, original_filename = _split_path(path)
            add_doc(index_writer=index_writer, path=path)

    index_writer.commit()


def get_index_dir(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    return os.path.join(
        bib_dir, Bibliography.HIDDEN_WORK_DIRNAME, INDEX_DIRNAME
    )


def list_entries(bib_dir):
    ix = whoosh.index.open_dir(get_index_dir(bib_dir))
    all_documents = ix.searcher().documents()
    out = []
    for document in all_documents:
        out.append(document["path"])
    return out


def _split_path(path):
    p = str(path)
    p, filename = os.path.split(p)
    p, ocr_dir = os.path.split(p)
    assert ocr_dir == "ocr"
    p, citekey = os.path.split(p)
    original_filename, tar_ext = os.path.splitext(filename)
    assert tar_ext == ".tar"
    return citekey, original_filename


class Search:
    def __init__(self, bib_dir):
        self.ix = whoosh.index.open_dir(get_index_dir(bib_dir))

    def search(self, querystring):
        qparser = whoosh.qparser.QueryParser("content", self.ix.schema)
        myquery = qparser.parse(querystring)
        out = []
        with self.ix.searcher() as searcher:
            hits = searcher.search(myquery)
            for hit in hits:
                citekey, original_filename = _split_path(hit["path"])
                out.append(
                    {
                        "citekey": citekey,
                        "original": original_filename,
                        "highlight": hit.highlights("content",),
                    }
                )
        return out

    def correct(self, mistyped_word):
        with self.ix.searcher() as searcher:
            corrector = searcher.corrector("content")
            print(corrector.suggest(mistyped_word, limit=3))
