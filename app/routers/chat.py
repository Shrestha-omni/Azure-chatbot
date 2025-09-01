# app/routers/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.embedder import Embedder
from app.services.vector_store.azure_vector_store import AzureVectorStore
from app.services.llm import AzureChatLLM
from langchain.schema import SystemMessage, HumanMessage
from app.config.settings import settings 
router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# Request body schema
class ChatRequest(BaseModel):
    query: str
    doc_id: Optional[int] = None  # Optional: restrict search to a specific document
    top_k: int = 5  # Number of chunks to fetch

class ChatResponse(BaseModel):
    answer: str
    context_chunks: List[str]

# Initialize services
embedder = Embedder()
vector_store = AzureVectorStore(
    endpoint=settings.azure_search_endpoint,
    key=settings.azure_search_api_key,
    index_name="documents" 
)
llm = AzureChatLLM()

@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        # Step 1: Embed the query
        query_embedding = embedder.embed_text(request.query)

        # Step 2: Search Azure Vector Store for top-k relevant chunks
        results = vector_store.search(
            query_embedding,
            k=request.top_k,
            #doc_id=request.doc_id  # pass doc_id for optional filtering at search level
        )

        # Extract content for context
        context_chunks = results

        # Step 3: Construct messages for LLM
        system_prompt = "You are a helpful assistant providing answers based on provided document context."
        context_text = "\n\n".join(context_chunks)
        user_prompt = f"Context:\n{context_text}\n\nQuestion: {request.query}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Step 4: Get response from LLM
        answer = llm.chat(messages)

        return ChatResponse(answer=answer, context_chunks=context_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")
