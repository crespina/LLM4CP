from app.data_processing.generate_vector_stores import VectorStoresConstructor
from configuration import config_parser

if __name__ == "__main__":
    parser = config_parser()
    args = parser.parse_args()

    vsc = VectorStoresConstructor(args)
    vsc.run()
