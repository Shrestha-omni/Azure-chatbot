
import logging
from app.config.settings import settings
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not installed, falling back to simple word splitter.")

class Chunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200, model: str = None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.model = model or settings.azure_openai_chat_deployment

        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.encoding_for_model(model)
            except KeyError:
                logging.warning(f"Tokenizer for model {model} not found. Falling back to cl100k_base.")
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = None  # fallback mode

    def chunk_text(self, text: str):
        """
        Splits text into overlapping chunks using tokens if available,
        otherwise falls back to word-based splitting.
        """
        if self.tokenizer:
            tokens = self.tokenizer.encode(text)
            chunks = []
            start = 0
            while start < len(tokens):
                end = start + self.chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                chunks.append(chunk_text)
                start += self.chunk_size - self.overlap
            return chunks
        else:
            # Simple word-based fallback
            words = text.split()
            chunks = []
            start = 0
            while start < len(words):
                end = start + self.chunk_size
                chunk = " ".join(words[start:end])
                chunks.append(chunk)
                start += self.chunk_size - self.overlap
            return chunks
