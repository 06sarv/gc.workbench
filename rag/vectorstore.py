from pathlib import Path
import chromadb
import os
import numpy as np

class GenomicsVectorStore:
    def __init__(self, collection_name="genomics_knowledge"):
        data_dir = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
        self.client = chromadb.PersistentClient(path=str(data_dir))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.gemini_client = None
        self.embedding_model = None

    def _get_gemini_client(self):
        if self.gemini_client is None:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.gemini_client = genai
        return self.gemini_client

    def _get_embedding(self, text: str) -> list:
        """Get embedding using Google's text embedding model."""
        try:
            genai = self._get_gemini_client()
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            # Fallback to local sentence-transformers if Gemini fails
            print(f"Warning: Gemini embedding failed ({e}), falling back to local model")
            return self._get_local_embedding(text)

    def _get_local_embedding(self, text: str) -> list:
        """Fallback to local sentence-transformers model."""
        try:
            if self.embedding_model is None:
                from sentence_transformers import SentenceTransformer
                # Use a lightweight model that's more compatible
                self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embedding = self.embedding_model.encode(text)
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        except Exception as e:
            print(f"Warning: Local embedding also failed: {e}")
            # Return a zero vector as last resort
            return [0.0] * 384  # Standard embedding dimension

    def similarity_search(self, query: str, k: int = 5):
        try:
            embedding = self._get_embedding(query)
            results = self.collection.query(query_embeddings=[embedding], n_results=k)
            docs = []
            for text, meta, score in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            ):
                docs.append({"content": text, "metadata": meta, "score": score})
            return docs
        except Exception as e:
            # Fallback: return empty results if all embedding methods fail
            print(f"Warning: All embedding methods failed: {e}")
            return []
