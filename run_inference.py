import os
import warnings

from llama_index.core.response.pprint_utils import pprint_response

from app.inference.inference import Inference
from configuration import config_parser


if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    parser = config_parser()
    args = parser.parse_args()

    agent = Inference(args=args)
    query = input("Question: ")
    while True:
        response = agent.query_llm(question=query)
        pprint_response(response, show_source=True)
        query = input("\nQuestion: ")
