import os
from time import sleep

from langchain.output_parsers import StructuredOutputParser
from llama_index.core import PromptTemplate, Document
from llama_index.core import VectorStoreIndex
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.core.output_parsers import LangchainOutputParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from tqdm import tqdm

from app.utils.data_utils import get_response_schema, problem_family


class Storage:
    def __init__(self, args):
        self.args = args
        self.output_parser = LangchainOutputParser(
            StructuredOutputParser.from_response_schemas(get_response_schema(query_config_dict={
                "name": "The name of the problem",
                "description": "A description of the problem",
                "variables": "All the decision variables in mathematical notation, followed by an explanation of what "
                             "they are in English",
                "constraints": "All the constraints in mathematical notation only",
                "objective": "The objective of the problem (minimize or maximize what value)"
            })))

        self.description_template = PromptTemplate(
            "You are an expert in high-level constraint modelling and solving discrete optimization problems. \n"
            "In particular, you know Minizinc. You are provided with one or several Minizinc models that represents a single classical "
            "problem in constraint programming. Your task is to identify what is the problem modelled and give a "
            "complete description of the problem to the user. \n"
            "This is the source code of the model(s):\n"
            "--------------\n"
            "{source_code}"
            "--------------\n"
            "The format of the answer should be without any variation a JSON-like format with the following keys and "
            "explanation of what the corresponding values should be:\n"
            "name: The name of the problem\n"
            "description: A description of the problem in English\n"
            "variables: A string containing the list of all the decision variables in mathematical notation, "
            "followed by an explanation of what they are in English\n"
            "constraints: A string containing the list of all the constraints in mathematical notation, followed by an "
            "explanation of what they are in English\n"
            "objective: The objective of the problem (minimize or maximize what value)"
        )

        self.qa_template = """\
        You are provided with a description of a constraint problem:
        {context_str}
        \n
        Generate {num_questions} realistic and practical user questions or scenarios that would be naturally answered 
        by solving the problem but do not necessarily use the traditional or classical context of the problem. 
        Think beyond the usual applications—use creative analogies or different contexts. The questions should 
        incorporate real-life constraints, preferences, and priorities that reflect the problem's structure. 
        For example, focus on specific goals the user wants to achieve, the constraints they face, and the trade-offs 
        they might need to consider. The questions should never incorporate the name of the given problem. You can 
        decide to incorporate numeric dummy data into the questions.
        \n
        The format of the answer should be without any variation a JSON with the following keys :\n
        question1 : The first question/scenario should be from a user very skilled in modelling and solving constraint 
        problems.
        question2 : The second question/scenario should be from a user that knows nothing about formal modelling and 
        solving constraint problems.
        question3 : The third question/scenario should be from a young user.
        question4 : The fourth question/scenario should be very short
        question5 : The fifth question/scenario should be very long and specific.
        """

        self.descriptor_model = Groq(model="llama3-70b-8192", api_key=args.groq_api_key,
                                     model_kwargs={"seed": 42}, temperature=0.1, output_parser=self.output_parser)
        self.qa_model = Groq(model="llama3-70b-8192", api_key=args.groq_api_key,
                             model_kwargs={"seed": 42}, temperature=0.1)

        self.embeddings_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

        self.documents = []
        self.index = None

    def run(self):
        for filename in tqdm(os.listdir(self.args.txt_path), desc="Generating descriptions"):
            file_path = os.path.join(self.args.txt_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()

                    prompt = self.description_template.format(source_code=file_content)
                    text_description = self.descriptor_model.complete(prompt=prompt, formatted=True)

                    cp_model = Document(
                        text=text_description.text,
                        metadata={
                            "problem_family": problem_family(os.path.splitext(filename)[0]),
                            "model_name": os.path.splitext(filename)[0],  # TODO: Drop this
                            "source_code": file_content  # TODO: If this doesn't contribute, drop it.
                        },
                        id_=os.path.splitext(filename)[0]
                    )

                    """
                    cp_model_document.excluded_embed_metadata_keys = ["source_code"]
                    # The source code won't be embedded, therefore won't be used on the retrieval-by-similarity process. 
                    """
                    """
                    cp_model_document.excluded_llm_metadata_keys = ["source_code"]
                    # the source code won't be seen by the LLM during the inference/answer synthesis procedure,
                    # therefore the LLM won't be able to produce code based on this.
                    """

                    self.documents.append(cp_model)
                    sleep(3)

        self.index = VectorStoreIndex.from_documents(documents=self.documents,
                                                     transformations=[
                                                         QuestionsAnsweredExtractor(
                                                             llm=self.qa_model,
                                                             prompt_template=self.qa_template,
                                                             questions=5,
                                                             num_workers=1,
                                                             show_progress=False
                                                         )],
                                                     embed_model=self.embeddings_model,
                                                     show_progress=True)

        self.index.storage_context.persist(persist_dir=self.args.storage_dir)
