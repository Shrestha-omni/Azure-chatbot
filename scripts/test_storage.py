from app.services.storage_manager import StorageManager

def main():
    storage = StorageManager()

    # Upload test
    storage.upload_file("README.md", "test/readme_copy.md")

    # List test
    print("Files:", storage.list_files("test/"))

    # Download test
    storage.download_file("test/readme_copy.md", "downloaded_readme.md")


if __name__ == "__main__":
    main()
