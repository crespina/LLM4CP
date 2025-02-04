import os

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def load_index(args):
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

    Settings.show_progress = False

    if os.path.exists(args.storage_dir):
        storage_context = StorageContext.from_defaults(persist_dir=args.storage_dir)
        index = load_index_from_storage(storage_context, show_progress=False)
        print("Loaded index from storage.")
        return index
    else:
        print("Index storage directory not found. Parse and store the index first.")
        exit()
