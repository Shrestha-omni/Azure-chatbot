# app/routers/process.py

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pathlib import Path
from sqlalchemy.orm import Session
from app.config.settings import settings 
from app.services.storage_manager import StorageManager
from app.services.extractor import Extractor
from app.services.chunker import Chunker
from app.services.embedder import Embedder
from app.services.vector_store.azure_vector_store import AzureVectorStore
from app.state.repos import get_document_by_id
from app.state.db import get_db
router = APIRouter()

storage = StorageManager()
extractor = Extractor()
chunker = Chunker(chunk_size=1000, overlap=200, model="gpt-4")
embedder = Embedder()
vector_store = AzureVectorStore(
    endpoint=settings.azure_search_endpoint,
    key=settings.azure_search_api_key,
    index_name="documents" 
)

tmp_dir = Path("./data/tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)


@router.post("/{doc_id}")
async def process_document(doc_id: int, db: Session = Depends(get_db)):
    try:
        doc = get_document_by_id(db, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        local_path = tmp_dir / doc.name
        storage.download_file(blob_name=doc.blob_url, file_path=str(local_path))

        text = extractor.extract_text(str(local_path))
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text")

        chunks = chunker.chunk_text(text)
        embeddings = embedder.embed_batch(chunks)

        # chunks + metadata for indexing
        chunks_with_meta = [
            {"content": chunk, "doc_id": str(doc_id), "chunk_id": str(idx)}
            for idx, chunk in enumerate(chunks)
        ]

        ok = vector_store.add_embeddings(chunks_with_meta, embeddings)
        if not ok:
            raise HTTPException(status_code=500, detail="Indexing in Azure Cognitive Search failed.")

        return {
            "doc_id": doc_id,
            "num_chunks": len(chunks),
            "message": "Document processed and indexed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
