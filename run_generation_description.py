from app.data_processing.generate_descriptions import Description_Generator
from configuration import config_parser

if __name__ == "__main__":
    parser = config_parser()
    args = parser.parse_args()

    descriptor = Description_Generator(args)
    descriptor.run()    
