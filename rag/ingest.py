import yaml
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
CONFIG_PATH = Path(__file__).resolve().parent / "documents.yaml"

def load_sources():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]

def clean_html_content(content):
    """Clean HTML content to extract meaningful text."""
    from bs4 import BeautifulSoup
    import re

    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.decompose()

    # Remove common navigation and UI elements
    for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'menu']):
        element.decompose()

    # Remove elements with common UI classes/ids
    ui_selectors = [
        '[class*="nav"]', '[class*="menu"]', '[class*="header"]', '[class*="footer"]',
        '[class*="sidebar"]', '[class*="advertisement"]', '[class*="popup"]',
        '[id*="nav"]', '[id*="menu"]', '[id*="header"]', '[id*="footer"]'
    ]

    for selector in ui_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Get text content
    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # Remove very short content (likely navigation fragments)
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 20]
    text = '\n\n'.join(lines)

    return text

def fetch_documents(sources):
    docs = []
    for src in sources:
        try:
            print(f"Fetching {src['id']} from {src['url']}...")
            loader = WebBaseLoader([src["url"]])
            raw = loader.load()
            for doc in raw:
                # Clean the HTML content
                cleaned_content = clean_html_content(doc.page_content)
                if len(cleaned_content) > 100:  # Only keep substantial content
                    doc.page_content = cleaned_content
                    doc.metadata["source_id"] = src["id"]
                    doc.metadata["tags"] = src["tags"]
                    docs.append(doc)
            print(f"✓ Successfully fetched {src['id']}")
        except Exception as e:
            print(f"✗ Failed to fetch {src['id']}: {e}")
            continue
    return docs

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=200, separators=["\n\n", "\n", ". "]
    )
    return splitter.split_documents(documents)

def embed_chunks(chunks):
    """Embed chunks using Gemini API."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = []

    print(f"Embedding {len(texts)} chunks...")

    for i, text in enumerate(texts):
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
            if (i + 1) % 10 == 0:
                print(f"Embedded {i + 1}/{len(texts)} chunks")
        except Exception as e:
            print(f"Error embedding chunk {i}: {e}")
            # Use zero vector as fallback
            embeddings.append([0.0] * 768)  # Standard embedding dimension

    return embeddings

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DATA_DIR))
    collection = client.get_or_create_collection(
        name="genomics_knowledge",
        metadata={"hnsw:space": "cosine"}
    )

    sources = load_sources()
    documents = fetch_documents(sources)
    chunks = split_documents(documents)
    embeddings = embed_chunks(chunks)

    ids = [f"{chunk.metadata['source_id']}_{i}" for i, chunk in enumerate(chunks)]

    # Convert metadata to ChromaDB-compatible format
    metadatas = []
    for chunk in chunks:
        metadata = chunk.metadata.copy()
        # Convert tags list to string
        if 'tags' in metadata and isinstance(metadata['tags'], list):
            metadata['tags'] = ','.join(metadata['tags'])
        metadatas.append(metadata)

    texts = [chunk.page_content for chunk in chunks]

    # Ensure embeddings is a list of lists
    if not isinstance(embeddings, list) or (embeddings and not isinstance(embeddings[0], list)):
        embeddings = [e.tolist() if hasattr(e, 'tolist') else e for e in embeddings]
    
    collection.upsert(ids=ids, metadatas=metadatas, documents=texts, embeddings=embeddings)
    print(f"Ingested {len(texts)} chunks into knowledge base.")

if __name__ == "__main__":
    main()
