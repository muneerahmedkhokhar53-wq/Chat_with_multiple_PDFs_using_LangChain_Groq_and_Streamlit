import unittest

from langchain_core.documents import Document

from app import format_sources, split_documents


class DocumentPipelineTests(unittest.TestCase):
    def test_split_documents_preserves_source_metadata(self):
        source = Document(
            page_content=("A sentence about robotics and automation. " * 100),
            metadata={"source": "robotics.pdf", "page": 3},
        )
        chunks = split_documents([source])

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.metadata["source"] == "robotics.pdf" for chunk in chunks))
        self.assertTrue(all(chunk.metadata["page"] == 3 for chunk in chunks))
        self.assertTrue(all("start_index" in chunk.metadata for chunk in chunks))

    def test_empty_document_collection_returns_empty_chunks(self):
        self.assertEqual(split_documents([]), [])

    def test_format_sources_deduplicates_file_and_page(self):
        docs = [
            Document(page_content="a", metadata={"source": "paper.pdf", "page": 2}),
            Document(page_content="b", metadata={"source": "paper.pdf", "page": 2}),
            Document(page_content="c", metadata={"source": "paper.pdf", "page": 4}),
        ]

        self.assertEqual(
            format_sources(docs),
            ["paper.pdf — page 2", "paper.pdf — page 4"],
        )


if __name__ == "__main__":
    unittest.main()
