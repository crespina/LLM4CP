"""
Config object that handles the various parameters and configurations of the system.
"""

import os

import configargparse
from dotenv import load_dotenv

os.makedirs('./app/assets/env/', exist_ok=True)
load_dotenv(dotenv_path='./app/assets/env/.env')


def config_parser():
    parser = configargparse.ArgumentParser(
        description="LLM 4 CP.")
    parser.add_argument('--config', is_config_file=True,
                        help='config file path')

    # I/O params
    parser.add_argument('--storage_dir', type=str,
                        default='./data/vector_dbs/code_as_text/medium',
                        help='Vector DB directory path.')

    parser.add_argument('--output_dir', type=str,
                        default='./data/output',
                        help='Output directory path.')

    parser.add_argument('--results_dir', type=str,
                        default='./data/results',
                        help='Results directory path.')

    parser.add_argument('--mixed_db_txt', type=str,
                        default="./data/input/merged_mzn_source_code",
                        help='.txt directory input path.')

    parser.add_argument("--descriptions_dir", type=str,
                        default="data/output/generated_descriptions",
                        help="path of the folder containing the generated descriptions")

    parser.add_argument("--merged_mzn_source_path", type=str,
                        default="./data/input/merged_mzn_source_code",
                        help="path to the merged MiniZinc source code files")

    # Deployment
    parser.add_argument('--prod', action='store_true', help='Run in production mode')

    # API Keys
    parser.add_argument('--groq_api_key', type=str,
                        default=os.environ.get('GROQ_API_KEY'),
                        help='Your Groq API token key gsk_<...>)')

    return parser
