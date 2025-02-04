"""
Augustin CRESPIN
augustin.crespin@student.uclouvain.be | crespin.augustin@gmail.com

Ioannis KOSTIS
ioannis.kostis@uclouvain.be | ioannis.aris.kostis@gmail.com

Config object that handles the various parameters and configurations of the system.
"""

import configargparse


def config_parser():
    parser = configargparse.ArgumentParser(
        description="LLM 4 CP.")
    parser.add_argument('--config', is_config_file=True,
                        help='config file path')
    parser.add_argument("--keys", is_config_file=True, required=False,
                        help='Path to the API keys file.',
                        default='./app/assets/.api_keys/keys.txt')

    # I/O params
    parser.add_argument('--mzn_path', type=str,
                        default="./data/csplib_input/mzn",
                        help='.mzn directory input path.')
    parser.add_argument('--txt_path', type=str,
                        default="./data/csplib_input/txt",
                        help='.txt directory input path.')
    parser.add_argument('--storage_dir', type=str,
                        default='./data/vector_dbs/csplib_db',
                        help='Vector DB directory path.')
    parser.add_argument('--like_dislike_json_path', type=str,
                        default="./data/output/like_dislike.json",
                        help='.json like/dislike path')
    parser.add_argument("--like_dislike_csv_path", type=str,
                        default="./data/output/like_dislike.csv",
                        help=".csv like/dislike path")
    parser.add_argument("--output_path", type=str,
                        default="./data/output",
                        help="output path")

    # API Keys
    parser.add_argument('--llama_parse_key', type=str, help='Your LlamaParse token key (llx-<...>)')
    parser.add_argument('--openai_api_key', type=str, help='Your OPENAI API token key (sk-<...>)')
    parser.add_argument('--groq_api_key', type=str, help='Your Groq API token key gsk_<...>)')
    parser.add_argument('--cohere_api_key', type=str, help='Your Cohere API token key <...>)')

    # Database
    parser.add_argument("--db_name", type=str, default="llm4cp", help="Name of the database")
    parser.add_argument("--db_user", type=str, default="postgres", help="User owning the database")
    parser.add_argument("--db_host", type=str, default="localhost", help="Where the database is hosted")
    parser.add_argument('--db_password', type=str, help='Your database password <...>)')
    parser.add_argument("--db_port", type=int, default=5432, help="The port used by the database")

    return parser
