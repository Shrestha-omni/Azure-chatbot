from azure.storage.blob import BlobServiceClient
from app.config.settings import settings
from loguru import logger

class StorageManager:
    def __init__(self):
        try:
            # Build connection string dynamically from settings
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={settings.azure_storage_account};"
                f"AccountKey={settings.azure_storage_key};"
                f"EndpointSuffix=core.windows.net"
            )

            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = self.blob_service_client.get_container_client(
                settings.azure_storage_container
            )
            logger.info("✅ Connected to Azure Blob Storage")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Azure Blob Storage: {e}")
            raise

    def upload_file(self, file_path: str, blob_name: str):
        try:
            with open(file_path, "rb") as f:
                self.container_client.upload_blob(name=blob_name, data=f, overwrite=True)
            logger.info(f"✅ Uploaded {blob_name}")
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")

    def download_file(self, blob_name: str, file_path: str):
        try:
            blob = self.container_client.download_blob(blob_name)
            with open(file_path, "wb") as f:
                f.write(blob.readall())
            logger.info(f"✅ Downloaded {blob_name}")
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")

    def list_files(self, prefix: str = ""):
        try:
            return [blob.name for blob in self.container_client.list_blobs(name_starts_with=prefix)]
            #logger.info(f"📂 Blobs in container: {blobs}")
            #return blobs
        except Exception as e:
            logger.error(f"❌ List files failed: {e}")
            return []
