import whoosh
import whoosh.fields
import whoosh.index
import whoosh.query
import whoosh.qparser
import os
import glob
from . import Reader


def _make_path(citekey, original_filename, pagenumber):
    return str.join(
        "/", [citekey, original_filename, "{:06d}".format(pagenumber)]
    )


def init(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    index_dir = os.path.join(
        bib_dir, ".bibliography_organizer", "full_text_search_index"
    )
    os.makedirs(index_dir, exist_ok=True)

    index_schema = whoosh.fields.Schema(
        content=whoosh.fields.TEXT, path=whoosh.fields.ID(stored=True),
    )

    ix = whoosh.index.create_in(index_dir, index_schema)


def _open(bib_dir):
    bib_dir = os.path.normpath(bib_dir)
    index_dir = os.path.join(
        bib_dir, ".bibliography_organizer", "full_text_search_index"
    )
    return whoosh.index.open_dir(index_dir)


def add_entry(bib_dir, citekey):
    bib_dir = os.path.normpath(bib_dir)
    entry_dir = os.path.join(bib_dir, citekey)
    entry_dir = os.path.normpath(entry_dir)

    ix = _open(bib_dir=bib_dir)
    writer = ix.writer()

    orc_wildcard = os.path.join(entry_dir, "ocr", "*.tar")
    for string_archive_path in glob.glob(orc_wildcard):
        filename = os.path.basename(string_archive_path)
        original_filename = os.path.splitext(filename)[0]
        arc = Reader.read_string_archive(path=string_archive_path)

        for pagenumber in arc:
            writer.add_document(
                content=arc[pagenumber],
                path=_make_path(
                    citekey=citekey,
                    original_filename=original_filename,
                    pagenumber=pagenumber,
                ),
            )
    writer.commit()


def list_entries(bib_dir):
    ix = _open(bib_dir)
    all_documents = ix.searcher().documents()
    out = []
    for document in all_documents:
        out.append(document["path"])
    return out


class Search:
    def __init__(self, bib_dir):
        self.ix = _open(bib_dir=bib_dir)

    def search(self, querystring):
        qparser = whoosh.qparser.QueryParser("content", self.ix.schema)
        myquery = qparser.parse(querystring)
        out = []
        with self.ix.searcher() as searcher:
            hits = searcher.search(myquery)
            for hit in hits:
                citekey, original_filename, pagenumber = str.split(
                    hit["path"], "/"
                )
                out.append(
                    {
                        "citekey": citekey,
                        "original": original_filename,
                        "pagenumber": int(pagenumber),
                    }
                )
        return out

    def correct(self, mistyped_word):
        with self.ix.searcher() as searcher:
            corrector = searcher.corrector("content")
            print(corrector.suggest(mistyped_word, limit=3))
