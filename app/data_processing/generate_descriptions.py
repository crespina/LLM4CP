import os
from time import sleep

from llama_index.core import PromptTemplate, Document
from llama_index.core import VectorStoreIndex
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from tqdm import tqdm

from app.utils.data_utils import problem_family
from app.utils.throttle import throttle_requests
from configuration import config_parser
from llama_index.core.callbacks import TokenCountingHandler, CallbackManager
from llama_index.core import Settings

class Description_Generator:
    def __init__(self,args):

        self.args = args

        self.template_description_level_expert = PromptTemplate(
            "You are an expert in high-level constraint modeling and solving discrete optimization problems. \n"
            "In particular, you know Minizinc. You are provided with one or several Minizinc models that represents a single classical "
            "problem in constraint programming. Your task is to identify what is the problem modeled and give a "
            "complete description of the problem to the user. \n"
            "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
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
            "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
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
            "You are given one or more Minizinc models that represent a single classical constraint programming problem."
            "Your task is to read the code and explain what the problem is about using very simple language."
            "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
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

        self.descriptor_model = Groq(
            model="llama3-70b-8192",
            api_key=args.groq_api_key,
            model_kwargs={"seed": 19851900},
            temperature=0.1
        )
        self.token_counter = TokenCountingHandler()
        self.callback_manager = CallbackManager([self.token_counter])
        Settings.callback_manager = self.callback_manager
        self.descriptor_model.callback_manager = Settings.callback_manager
        self.model_tpd = 30_000

    @throttle_requests()
    def run(self):
        for filename in tqdm(os.listdir(self.args.mixed_db_txt), desc="Generating descriptions"):
            file_path = os.path.join(self.args.mixed_db_txt, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                    filename_stripped = filename[:4]

                    prompt_expert = self.template_description_level_expert.format(
                        source_code=file_content
                    )
                    prompt_medium = self.template_description_level_medium.format(
                        source_code=file_content
                    )
                    prompt_beginner = self.template_description_level_beginner.format(
                        source_code=file_content
                    )

                    text_description_expert = self.descriptor_model.complete(
                        prompt=prompt_expert
                    ).text
                    text_description_medium = self.descriptor_model.complete(
                        prompt=prompt_medium
                    ).text
                    text_description_beginner = self.descriptor_model.complete(
                        prompt=prompt_beginner
                    ).text

                    output_folder = os.path.join("data/generated_descriptions", filename_stripped)

                    os.makedirs(output_folder, exist_ok=True)

                    with open(os.path.join(output_folder, "expert.txt"), "w", encoding="utf-8") as f:
                        f.write(text_description_expert)

                    with open(os.path.join(output_folder, "medium.txt"), "w", encoding="utf-8") as f:
                        f.write(text_description_medium)

                    with open(os.path.join(output_folder, "beginner.txt"), "w", encoding="utf-8") as f:
                        f.write(text_description_beginner)

                    with open(os.path.join(output_folder, "source_code.txt"), "w", encoding="utf-8") as f:
                        f.write(file_content)
