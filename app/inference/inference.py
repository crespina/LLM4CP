from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.data_processing.data_loaders import load_index


class Inference:
    def __init__(self, args):
        self.index = load_index(args)
        self.embedding_model = HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base",
                                                    trust_remote_code=True)

    def retrieve_nodes(self, question):
        try:
            query_engine = self.index.as_retriever(similarity_top_k=5)
            nodes = query_engine.retrieve(question)
            return nodes
        except Exception as e:
            return e
