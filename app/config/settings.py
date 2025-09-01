from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Azure Storage
    azure_storage_account: str = Field(..., alias="AZURE_STORAGE_ACCOUNT_NAME")
    azure_storage_key: str = Field(..., alias="AZURE_STORAGE_ACCOUNT_KEY")
    azure_storage_container: str = Field(..., alias="AZURE_STORAGE_CONTAINER_NAME")

    # Azure OpenAI
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_embedding_deployment: str = Field(..., alias="AZURE_OPENAI_EMBED_MODEL")
    azure_openai_chat_deployment: str = Field(..., alias="AZURE_OPENAI_CHAT_MODEL")

    # Azure Cognitive Search
    azure_search_endpoint: str = Field(..., alias="AZURE_SEARCH_ENDPOINT")
    azure_search_api_key: str = Field(..., alias="AZURE_SEARCH_API_KEY")
    azure_search_index_name: str = Field(..., alias="AZURE_SEARCH_INDEX_NAME")

    # SQLite
    sqlite_path: str = Field("sqlite:///./db.sqlite3", alias="SQLITE_PATH")

    # FAISS
    faiss_index_dir: str = Field("./faiss_index", alias="FAISS_INDEX_DIR")

    class Config:
        env_file = ".env"
        populate_by_name = True


# Initialize settings
settings = Settings()
