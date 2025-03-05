import os

from llama_index.core import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Settings

class VectorStoresConstructor:

    def __init__(self, args):

        self.args = args

        self.embeddings_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

        self.docs_code_only = []
        self.docs_expert = []
        self.docs_medium = []
        self.docs_beginner = []
        self.docs_beginner_medium = []
        self.docs_beginner_expert = []
        self.docs_medium_expert = []
        self.docs_beginner_medium_expert = []

        self.index_code_only = None
        self.index_expert = None
        self.index_medium = None
        self.index_beginner = None
        self.index_beginner_medium = None
        self.index_beginner_expert = None
        self.index_medium_expert = None
        self.index_beginner_medium_expert = None

        self.storage_dir_code_only = self.args.storage_dir + "/code"
        self.storage_dir_expert = self.args.storage_dir + "/expert"
        self.storage_dir_medium = self.args.storage_dir + "/medium"
        self.storage_dir_beginner = self.args.storage_dir + "/beginner"
        self.storage_dir_beginner_medium = self.args.storage_dir + "/beginnermedium"
        self.storage_dir_beginner_expert = self.args.storage_dir + "/beginnerexpert"
        self.storage_dir_medium_expert = self.args.storage_dir + "/mediumexpert"
        self.storage_dir_beginner_medium_expert = self.args.storage_dir + "/beginnermediumexpert"

    def run(self):

        Settings.chunk_size = 4096

        for folder_name in os.listdir(self.args.descriptions_folder):
            folder_path = os.path.join(self.args.descriptions_folder, folder_name)
            if os.path.isdir(folder_path):

                expert_path = os.path.join(folder_path, "expert.txt")
                medium_path = os.path.join(folder_path, "medium.txt")
                beginner_path = os.path.join(folder_path, "beginner.txt")
                source_code_path = os.path.join(folder_path, "source_code.txt")

                with open(expert_path, "r", encoding="utf-8") as f:
                    text_description_expert = f.read()
                with open(medium_path, "r", encoding="utf-8") as f:
                    text_description_medium = f.read()
                with open(beginner_path, "r", encoding="utf-8") as f:
                    text_description_beginner = f.read()
                with open(source_code_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                base_name = os.path.splitext(folder_name)[0]

                text_description_beginner_medium = f"""Description 1:
                    ------
                    {text_description_beginner}
                    ======
                    Description 2:
                    ---------
                    {text_description_medium}"""

                text_description_beginner_expert = f"""Description 1:
                    ------
                    {text_description_beginner}
                    ======
                    Description 2:
                    ---------
                    {text_description_expert}"""

                text_description_medium_expert = f"""Description 1:
                    ------
                    {text_description_medium}
                    ======
                    Description 2:
                    ---------
                    {text_description_expert}"""

                text_description_beginner_medium_expert = f"""Description 1:
                    ------
                    {text_description_beginner}
                    ======
                    Description 2:
                    ---------
                    {text_description_medium}
                    ======
                    Description 3:
                    ---------
                    {text_description_expert}"""

                doc_source_code = Document(
                    text=source_code,
                    id_=base_name + "_source_code",
                )

                doc_beginner = Document(
                    text=text_description_beginner,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_beginner",
                )

                doc_medium = Document(
                    text=text_description_medium,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_medium",
                )

                doc_expert = Document(
                    text=text_description_expert,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_expert",
                )

                doc_beginner_medium = Document(
                    text=text_description_beginner_medium,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_beginner_medium",
                )

                doc_beginner_expert = Document(
                    text=text_description_beginner_expert,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_beginner_expert",
                )

                doc_medium_expert = Document(
                    text=text_description_medium_expert,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_medium_expert",
                )

                doc_beginner_medium_expert = Document(
                    text=text_description_beginner_medium_expert,
                    metadata={
                        "model_name": base_name,
                        "source_code": source_code,
                    },
                    id_=base_name + "_beginner_medium_expert",
                )

                self.docs_code_only.append(doc_source_code)
                self.docs_beginner.append(doc_beginner)
                self.docs_medium.append(doc_medium)
                self.docs_expert.append(doc_expert)
                self.docs_beginner_medium.append(doc_beginner_medium)
                self.docs_beginner_expert.append(doc_beginner_expert)
                self.docs_medium_expert.append(doc_medium_expert)
                self.docs_beginner_medium_expert.append(doc_beginner_medium_expert)

        self.index_code_only = VectorStoreIndex.from_documents(
            documents=self.docs_code_only,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_expert = VectorStoreIndex.from_documents(
            documents=self.docs_expert,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_medium = VectorStoreIndex.from_documents(
            documents=self.docs_medium,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_beginner = VectorStoreIndex.from_documents(
            documents=self.docs_beginner,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_beginner_medium = VectorStoreIndex.from_documents(
            documents=self.docs_beginner_medium,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_beginner_expert = VectorStoreIndex.from_documents(
            documents=self.docs_beginner_expert,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_medium_expert = VectorStoreIndex.from_documents(
            documents=self.docs_medium_expert,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        ) 

        self.index_beginner_medium_expert = VectorStoreIndex.from_documents(
            documents=self.docs_beginner_medium_expert,
            embed_model=self.embeddings_model,
            show_progress=True,
            chunk_size=2048,
        )

        self.index_code_only.storage_context.persist(persist_dir=self.storage_dir_code_only)
        self.index_expert.storage_context.persist(persist_dir=self.storage_dir_expert)
        self.index_medium.storage_context.persist(persist_dir=self.storage_dir_medium)
        self.index_beginner.storage_context.persist(persist_dir=self.storage_dir_beginner) 
        self.index_beginner_medium.storage_context.persist(persist_dir=self.storage_dir_beginner_medium)
        self.index_beginner_expert.storage_context.persist(persist_dir=self.storage_dir_beginner_expert)
        self.index_medium_expert.storage_context.persist(persist_dir=self.storage_dir_medium_expert)
        self.index_beginner_medium_expert.storage_context.persist(persist_dir=self.storage_dir_beginner_medium_expert)
