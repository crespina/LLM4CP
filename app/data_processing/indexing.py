import os
from time import sleep

from langchain.output_parsers import StructuredOutputParser
from llama_index.core import PromptTemplate, Document
from llama_index.core import VectorStoreIndex
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from tqdm import tqdm

from app.utils.data_utils import problem_family
from app.utils.throttle import throttle_requests

class Storage:
    def __init__(self, args):
        self.args = args

        self.template_description_level_expert = PromptTemplate(
            "You are an expert in high-level constraint modeling and solving discrete optimization problems. \n"
            "In particular, you know Minizinc. You are provided with one or several Minizinc models that represents a single classical "
            "problem in constraint programming. Your task is to identify what is the problem modeled and give a "
            "complete description of the problem to the user. \n"
            "This is the source code of the model(s):\n"
            "--------------\n"
            "{source_code}"
            "\n--------------\n"
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

        self.template_description_level_medium = PromptTemplate(
            "You are experienced in constraint programming and familiar with Minizinc."
            "You are provided with one or more Minizinc models representing a classic constraint programming problem."
            "Your task is to identify the problem and explain it in clear, intermediate-level language."
            "Assume the reader has some technical background but is not an expert."
            "In your explanation, please include:\n"
            "The name of the problem.\n"
            "A concise description of what the problem is about.\n"
            "An explanation of the main decision variables and what they represent.\n"
            "A description of the key constraints in plain language (avoid heavy mathematical notation).\n"
            "An explanation of the problem's objective (what is being minimized or maximized).\n"
            "Here is the source code of the model(s):"
            "--------------\n"
            "{source_code}"
            "\n--------------\n"
        )

        self.template_description_level_beginner = PromptTemplate(
            "You are given one or more Minizinc models that represent a classical constraint programming problem."
            "Your task is to read the code and explain what the problem is about using very simple language."
            "Assume the reader does not have much background in programming or mathematics."
            "Please explain:\n"
            "The name of the problem.\n"
            "What the problem is about in everyday terms.\n"
            "What the main variables are and what they mean, using plain language.\n"
            "What the basic restrictions or rules of the problem are, explained simply.\n"
            "What the goal of the problem is (for example, what you want to minimize or maximize).\n"
            "Here is the source code:\n"
            "--------------\n"
            "{source_code}"
            "--------------\n"
        )

        self.descriptor_model = Groq(model="llama3-70b-8192", api_key=args.groq_api_key,
                                     model_kwargs={"seed": 42}, temperature=0.1, output_parser=self.output_parser)

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
