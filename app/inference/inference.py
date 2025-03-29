from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core import PromptTemplate

from app.data_processing.data_loaders import load_index


class Inference:
    def __init__(self, args):
        self.model = Groq(
            model="llama3-70b-8192",
            api_key=args.groq_api_key,
            model_kwargs={"seed": 19851900},
            temperature=0.1,
        )

        self.index = load_index(args)
        self.embedding_model = HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base", trust_remote_code=True)
        self.reranker = CohereRerank(api_key=args.cohere_api_key, top_n=5)

    def query_llm(self, question):
        try : 
            query_engine = self.index.as_query_engine(llm=self.model,
                                                  similarity_top_k=22,
                                                  node_postprocessors=[self.reranker])
            response = query_engine.query(question)
            return response
        except Exception as e :
            return e
