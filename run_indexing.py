from MnZcDescriptor.app.data_processing.indexing import Storage
from MnZcDescriptor.configuration import config_parser

if __name__ == "__main__":
    parser = config_parser()
    args = parser.parse_args()

    storage_agent = Storage(args=args)
    storage_agent.run()
