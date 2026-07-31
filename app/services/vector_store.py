"""Vector storage layer for LearnTwin AI using ChromaDB."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from app.core.config import settings


class VectorStore:
    """Persistent vector store wrapper for ChromaDB collections."""

    def __init__(self, collection_name: str = "learntwin_documents") -> None:
        self.logger = logging.getLogger(__name__)
        self.persist_directory: Path = settings.CHROMA_PATH
        self.collection_name = collection_name
        self._client = self._create_client()
        self.collection = self._get_or_create_collection()

    def _create_client(self) -> chromadb.api.Client:
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        settings_obj = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.persist_directory),
        )
        return chromadb.Client(settings_obj)

    def _get_or_create_collection(self) -> Any:
        try:
            return self._client.get_or_create_collection(name=self.collection_name)
        except Exception as exc:
            self.logger.error(
                "Unable to initialize ChromaDB collection '%s': %s",
                self.collection_name,
                exc,
            )
            raise

    def add_document(self, document_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """Add or update a document in the vector store.

        Args:
            document_id: Unique identifier for the document.
            text: The text content to store.
            metadata: Arbitrary metadata associated with the document.
        """
        try:
            self.collection.upsert(
                ids=[document_id],
                documents=[text],
                metadatas=[metadata],
            )
            self.logger.debug(
                "Stored document %s in ChromaDB collection %s",
                document_id,
                self.collection_name,
            )
        except Exception as exc:
            self.logger.error(
                "Failed to add document %s to ChromaDB: %s",
                document_id,
                exc,
            )

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the collection for similar documents.

        Args:
            query_text: Text to search for.
            top_k: Maximum number of results to return.

        Returns:
            List of matching documents with metadata and distance values.
        """
        try:
            results = self.collection.query(query_texts=[query_text], n_results=top_k)
        except Exception as exc:
            self.logger.error("ChromaDB query failed: %s", exc)
            return []

        if not isinstance(results, dict):
            self.logger.error("Unexpected ChromaDB query response type: %s", type(results))
            return []

        ids = self._safe_extract(results, "ids")
        documents = self._safe_extract(results, "documents")
        metadatas = self._safe_extract(results, "metadatas")
        distances = self._safe_extract(results, "distances")

        if not ids or not ids[0]:
            return []

        output: List[Dict[str, Any]] = []
        for index, document_id in enumerate(ids[0]):
            output.append(
                {
                    "document_id": str(document_id),
                    "text": str(documents[0][index]) if documents and documents[0] else "",
                    "metadata": metadatas[0][index] if metadatas and metadatas[0] else {},
                    "distance": float(distances[0][index]) if distances and distances[0] else None,
                }
            )

        return output

    def delete_document(self, document_id: str) -> bool:
        """Remove a document from the collection by its identifier.

        Args:
            document_id: Unique document identifier.

        Returns:
            True when deletion succeeds, False when the document is missing or deletion fails.
        """
        try:
            self.collection.delete(ids=[document_id])
            self.logger.debug("Deleted document %s from ChromaDB", document_id)
            return True
        except Exception as exc:
            self.logger.warning(
                "ChromaDB delete failed for document %s: %s",
                document_id,
                exc,
            )
            return False

    def count(self) -> int:
        """Return the number of documents stored in the collection."""
        try:
            total = self.collection.count()
            return int(total)
        except Exception as exc:
            self.logger.error("ChromaDB count failed: %s", exc)
            return 0

    @staticmethod
    def _safe_extract(payload: dict, key: str) -> List[Any]:
        raw = payload.get(key)
        if isinstance(raw, list):
            return raw
        return []
