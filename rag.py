import os
import shutil
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from pypdf import PdfReader
import docx

class RecursiveCharacterTextSplitter:
    """
    Pure Python implementation of RecursiveCharacterTextSplitter to prevent
    dependency version mismatches and import errors.
    """
    def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=len):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.separators = ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> list:
        if not text:
            return []
            
        def _split(text_to_split: str, separators: list) -> list:
            if not text_to_split:
                return []
            
            separator = separators[0] if separators else ""
            next_separators = separators[1:] if len(separators) > 1 else []
            
            splits = text_to_split.split(separator) if separator else list(text_to_split)
            
            good_splits = []
            current_chunk = []
            current_len = 0
            
            for s in splits:
                s_len = self.length_function(s)
                if current_len + s_len + (len(separator) if current_chunk else 0) <= self.chunk_size:
                    current_chunk.append(s)
                    current_len += s_len + (len(separator) if len(current_chunk) > 1 else 0)
                else:
                    if current_chunk:
                        good_splits.append(separator.join(current_chunk))
                    
                    if s_len > self.chunk_size:
                        if next_separators:
                            good_splits.extend(_split(s, next_separators))
                        else:
                            good_splits.append(s)
                    
                    overlap_splits = []
                    overlap_len = 0
                    for prev_s in reversed(current_chunk):
                        prev_len = self.length_function(prev_s)
                        if overlap_len + prev_len + (len(separator) if overlap_splits else 0) <= self.chunk_overlap:
                            overlap_splits.insert(0, prev_s)
                            overlap_len += prev_len + (len(separator) if len(overlap_splits) > 1 else 0)
                        else:
                            break
                    
                    current_chunk = overlap_splits + [s]
                    current_len = overlap_len + s_len + (len(separator) if len(current_chunk) > 1 else 0)
            
            if current_chunk:
                good_splits.append(separator.join(current_chunk))
                
            return good_splits
            
        return _split(text, self.separators)


# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Create folders if they do not exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

class SentenceTransformersEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function using SentenceTransformers for ChromaDB
    to prevent dependency version mismatches.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(input, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

class RAGEngine:
    """
    Handles file parsing, text chunking, local vector storage, and semantic searches
    using ChromaDB and SentenceTransformers.
    """
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embedding_fn = SentenceTransformersEmbeddingFunction()
        self.collection_name = "naac_documentation"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extracts text from a PDF document using pypdf."""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extracts text from a DOCX file using python-docx."""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
        return text

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extracts text from a plain TXT file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return ""

    def load_and_index_file(self, file_path: str) -> bool:
        """
        Parses a file, splits its content into semantic chunks, generates embeddings,
        and saves them in ChromaDB.
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # 1. Extract text
        if ext == ".pdf":
            text = self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = self.extract_text_from_docx(file_path)
        elif ext == ".txt":
            text = self.extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return False

        if not text.strip():
            print(f"No text extracted from {filename}")
            return False

        # 2. Chunk text
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return False

        # 3. Delete existing chunks for this specific file first to avoid duplicates
        self.collection.delete(where={"source": filename})

        # 4. Prepare data for insertion
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        
        # 5. Insert chunks
        # ChromaDB allows batching, for extremely large files we insert in sub-batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end = i + batch_size
            self.collection.add(
                ids=ids[i:end],
                documents=chunks[i:end],
                metadatas=metadatas[i:end]
            )

        print(f"Indexed {len(chunks)} chunks from {filename} successfully.")
        return True

    def delete_document(self, filename: str) -> bool:
        """Deletes a document from the collection and removes the local file."""
        try:
            # Delete from database
            self.collection.delete(where={"source": filename})
            
            # Delete from filesystem
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting document {filename}: {e}")
            return False

    def get_indexed_documents(self) -> list:
        """Returns a list of unique filenames indexed in ChromaDB."""
        try:
            results = self.collection.get(include=["metadatas"])
            if not results or not results["metadatas"]:
                return []
            
            # Extract unique sources
            sources = set()
            for meta in results["metadatas"]:
                if meta and "source" in meta:
                    sources.add(meta["source"])
            return sorted(list(sources))
        except Exception as e:
            print(f"Error fetching indexed documents: {e}")
            return []

    def get_total_chunks(self) -> int:
        """Returns the total number of document chunks currently in the database."""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error counting collection: {e}")
            return 0

    def query(self, query_text: str, n_results: int = 5) -> dict:
        """
        Queries ChromaDB for similar chunks and aggregates retrieved contexts and source lists.
        """
        if self.get_total_chunks() == 0:
            return {
                "context": "No relevant context found. No documents have been indexed yet.",
                "sources": []
            }
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            if not results or not results["documents"] or not results["documents"][0]:
                return {
                    "context": "No relevant context found.",
                    "sources": []
                }

            # Build context paragraph and list of sources
            retrieved_chunks = results["documents"][0]
            metadatas = results["metadatas"][0]
            
            context_pieces = []
            sources = set()
            
            for doc, meta in zip(retrieved_chunks, metadatas):
                source = meta.get("source", "Unknown Document") if meta else "Unknown Document"
                sources.add(source)
                context_pieces.append(f"[Source: {source}]\n{doc}")
                
            combined_context = "\n\n---\n\n".join(context_pieces)
            
            return {
                "context": combined_context,
                "sources": sorted(list(sources))
            }
        except Exception as e:
            print(f"Error querying RAG system: {e}")
            return {
                "context": f"Error querying RAG: {e}",
                "sources": []
            }
            
    def rebuild_db_from_documents_folder(self):
        """Walks through the documents folder and indexes all files."""
        if not os.path.exists(DOCUMENTS_DIR):
            return
        
        for filename in os.listdir(DOCUMENTS_DIR):
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            if os.path.isfile(file_path) and not filename.startswith("."):
                ext = os.path.splitext(filename)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    print(f"Re-indexing {filename}...")
                    self.load_and_index_file(file_path)
