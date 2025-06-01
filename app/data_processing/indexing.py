import os

from llama_index.core import PromptTemplate, Document
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.callbacks import TokenCountingHandler, CallbackManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from tqdm import tqdm

from app.utils.app_utils import throttle_requests
from app.utils.CONSTANTS import INDICES_EXP


class Storage:
    def __init__(self, args):
        self.args = args

        # Templates for description generation at different expertise levels
        self.templates = {
            "expert": PromptTemplate(
                "You are an expert in high-level constraint modeling and solving discrete optimization problems. \n"
                "In particular, you know Minizinc. You are provided with one or several Minizinc models that represents a single classical"
                "problem in constraint programming. Your task is to identify what is the problem modeled and give a "
                "complete description of the problem to the user. \n"
                "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
                "This is the source code of the model(s):\n"
                "--------------\n"
                "{source_code}"
                "\n--------------\n"
                "In your answer please explain:\n"
                "name: The name of the problem\n"
                "description: A description of the problem in English\n"
                "variables: A string containing the list of all the decision variables in mathematical notation, "
                "followed by an explanation of what they are in English\n"
                "constraints: A string containing the list of all the constraints in mathematical notation, followed by an "
                "explanation of what they are in English\n"
                "objective: The objective of the problem (minimize or maximize what value)\n"
                "In your answer, do not include any introductory phrases (such as 'Here is the explanation of the problem')"
            ),

            "medium": PromptTemplate(
                "You are experienced in constraint programming and familiar with Minizinc."
                "You are provided with one or more Minizinc models representing a classic constraint programming problem."
                "Your task is to identify the problem and explain it in clear, intermediate-level language."
                "Assume the reader has some technical background but is not an expert."
                "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
                "In your answer please explain:\n"
                "The name of the problem.\n"
                "A concise description of what the problem is about.\n"
                "An explanation of the main decision variables and what they represent.\n"
                "A description of the key constraints in plain language (avoid heavy mathematical notation).\n"
                "An explanation of the problem's objective (what is being minimized or maximized).\n"
                "In your answer, do not include any introductory phrases (such as 'Here is the explanation of the problem')"
                "Here is the source code of the model(s):"
                "--------------\n"
                "{source_code}"
                "\n--------------\n"
            ),

            "beginner": PromptTemplate(
                "You are given one or more Minizinc models that represent a single classical constraint programming problem."
                "Your task is to read the code and explain what the problem is about using very simple language."
                "If there are several models for the same problem, do not explain each one separately. Instead, focus on explaining the overall problem"
                "Assume the reader does not have much background in programming or mathematics."
                "In your answer please explain:\n"
                "The name of the problem.\n"
                "What the problem is about in everyday terms.\n"
                "What the main variables are and what they mean, using plain language.\n"
                "What the basic restrictions or rules of the problem are, explained simply.\n"
                "What the goal of the problem is (for example, what you want to minimize or maximize).\n"
                "In your answer, do not include any introductory phrases (such as 'Here is the explanation of the problem')"
                "Here is the source code:\n"
                "--------------\n"
                "{source_code}"
                "--------------\n"
            )
        }

        # Models setup
        self.descriptor_model = Groq(
            model="llama3-70b-8192",
            api_key=args.groq_api_key,
            model_kwargs={"seed": 42},
            temperature=0.0
        )

        self.embeddings_model = HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base")
        Settings.embed_model = self.embeddings_model

        # Token counting setup
        self.token_counter = TokenCountingHandler()
        self.callback_manager = CallbackManager([self.token_counter])
        Settings.callback_manager = self.callback_manager
        self.descriptor_model.callback_manager = Settings.callback_manager
        self.model_tpm = 30_000

        # Document collections
        self.expertise_levels = INDICES_EXP
        self.docs_collections = {level: [] for level in self.expertise_levels}

        # Storage directories for indices
        self.storage_dirs = {
            level: os.path.join("./data/vector_dbs/code_as_text", level)
            for level in self.expertise_levels
        }

    @throttle_requests()
    def generate_descriptions(self):
        """Generate problem descriptions at different expertise levels"""
        os.makedirs(self.args.descriptions_dir, exist_ok=True)

        for filename in tqdm(os.listdir(self.args.mixed_db_txt), desc="Generating descriptions"):
            file_path = os.path.join(self.args.mixed_db_txt, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                    filename_stripped = filename[:-4]

                    # Generate descriptions for different expertise levels
                    descriptions = {}
                    for level, template in self.templates.items():
                        prompt = template.format(source_code=file_content)
                        descriptions[level] = self.descriptor_model.complete(prompt=prompt).text

                    # Save descriptions to files
                    output_folder = os.path.join(self.args.descriptions_dir, filename_stripped)
                    os.makedirs(output_folder, exist_ok=True)

                    for level, description in descriptions.items():
                        with open(os.path.join(output_folder, f"{level}.txt"), "w", encoding="utf-8") as f:
                            f.write(description)

                    with open(os.path.join(output_folder, "source_code.txt"), "w", encoding="utf-8") as f:
                        f.write(file_content)

    def create_vector_stores(self):
        """Create vector stores from generated descriptions"""
        Settings.chunk_size = 4096

        for folder_name in os.listdir(self.args.descriptions_dir):
            folder_path = os.path.join(self.args.descriptions_dir, folder_name)
            if os.path.isdir(folder_path):
                # Read files
                files = {}
                for level in ["expert", "medium", "beginner", "source_code"]:
                    file_path = os.path.join(folder_path, f"{level}.txt")
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        files[level] = content

                base_name = os.path.splitext(folder_name)[0]
                self.create_documents(base_name, files)

        # Create and persist vector indices
        self.create_and_persist_indices()

    def create_documents_without_code(self, base_name, files):
        """Create different document combinations for indexing without source code"""
        
        # Create single expertise level documents
        for level in ["beginner", "medium", "expert"]:
            self.docs_collections[level].append(
                Document(
                    text=files[level],
                    metadata={"model_name": base_name},
                    id_=f"{base_name}_{level}",
                )
            )

        # Create combined expertise documents
        combinations = [
            ("beginner_medium", ["beginner", "medium"]),
            ("beginner_expert", ["beginner", "expert"]),
            ("medium_expert", ["medium", "expert"]),
            ("beginner_medium_expert", ["beginner", "medium", "expert"])
        ]

        for combo_name, levels in combinations:
            text_parts = []

            for i, level in enumerate(levels, 1):
                text_parts.append(f"Description {i}:\n------\n{files[level]}")

            combined_text = "\n======\n".join(text_parts)

            self.docs_collections[combo_name].append(
                Document(
                    text=combined_text,
                    metadata={"model_name": base_name},
                    id_=f"{base_name}_{combo_name}",
                )
            )

    def create_documents(self, base_name, files):
        """Create different document combinations for indexing"""
        source_code = files["source_code"]

        # Create code-only document
        self.docs_collections["code"].append(
            Document(
                text=source_code,
                metadata={"model_name": base_name},
                id_=f"{base_name}_source_code",
            )
        )

        # Create single expertise level documents
        for level in ["beginner", "medium", "expert"]:
            text = f"""Source code:
            ------
            {source_code}
            ======
            Description:
            ---------
            {files[level]}"""

            self.docs_collections[level].append(
                Document(
                    text=text,
                    metadata={"model_name": base_name},
                    id_=f"{base_name}_{level}",
                )
            )

        # Create combined expertise documents
        combinations = [
            ("beginner_medium", ["beginner", "medium"]),
            ("beginner_expert", ["beginner", "expert"]),
            ("medium_expert", ["medium", "expert"]),
            ("beginner_medium_expert", ["beginner", "medium", "expert"])
        ]

        for combo_name, levels in combinations:
            text_parts = [f"Source code:\n------\n{source_code}"]

            for i, level in enumerate(levels, 1):
                text_parts.append(f"Description {i}:\n------\n{files[level]}")

            combined_text = "\n======\n".join(text_parts)

            self.docs_collections[combo_name].append(
                Document(
                    text=combined_text,
                    metadata={"model_name": base_name},
                    id_=f"{base_name}_{combo_name}",
                )
            )

    def create_and_persist_indices(self):
        """Create vector indices and persist them to storage"""
        for level in self.expertise_levels:
            print(f"Creating index for {level}...")
            index = VectorStoreIndex.from_documents(
                documents=self.docs_collections[level],
                embed_model=self.embeddings_model,
                show_progress=True,
                chunk_size=4096,
            )

            # Persist index
            index.storage_context.persist(persist_dir=self.storage_dirs[level])
            print(f"Index for {level} persisted to {self.storage_dirs[level]}")

    def run(self):
        """Main execution method to generate descriptions and create vector stores"""
        # Step 1: Generate descriptions at different expertise levels
        self.generate_descriptions()

        # Step 2: Create vector stores from the generated descriptions
        self.create_vector_stores()
        #self.create_documents_without_code() #uncomment this to generate the embedding DBs without the source code

