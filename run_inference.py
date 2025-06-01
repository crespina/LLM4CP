import os
import warnings

from app.inference.inference import Inference
from app.utils.app_utils import pprint_ranking
from configuration import config_parser

if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    parser = config_parser()
    args = parser.parse_args()

    agent = Inference(args=args)

    while True:
        query = input("Question: ")
        nodes = agent.retrieve_nodes(question=query)
        pprint_ranking(nodes)
