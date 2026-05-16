import argparse
import os
from pathlib import Path

from openai import OpenAI


def main():
    parser = argparse.ArgumentParser(
        description="Create an OpenAI Vector Store and upload planning guideline files."
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to folder containing PDF/DOCX/MD/TXT files."
    )
    parser.add_argument(
        "--name",
        default="Planning_Knowledge_Base",
        help="Vector store name."
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set OPENAI_API_KEY before running this script.")

    folder = Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        raise RuntimeError(f"Folder not found: {folder}")

    allowed = {".pdf", ".docx", ".md", ".txt"}
    files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in allowed]

    if not files:
        raise RuntimeError("No supported files found. Supported: PDF, DOCX, MD, TXT")

    client = OpenAI(api_key=api_key)

    print(f"Creating vector store: {args.name}")
    vector_store = client.vector_stores.create(name=args.name)
    print(f"VECTOR_STORE_ID={vector_store.id}")

    print(f"Uploading {len(files)} files...")

    uploaded_file_ids = []
    for path in files:
        print(f"Uploading: {path}")
        with path.open("rb") as f:
            uploaded = client.files.create(
                file=f,
                purpose="assistants"
            )
            uploaded_file_ids.append(uploaded.id)

    print("Adding files to vector store and waiting for indexing...")
    batch = client.vector_stores.file_batches.create_and_poll(
        vector_store_id=vector_store.id,
        file_ids=uploaded_file_ids
    )

    print("Batch status:", batch.status)
    print("File counts:", batch.file_counts)
    print("\nCopy this value into Render Environment Variables:")
    print(f"OPENAI_VECTOR_STORE_ID={vector_store.id}")


if __name__ == "__main__":
    main()
