from datetime import datetime

from configuration import config_parser
from app.gui.gui import GUI

if __name__ == "__main__":
    print(f"Chat started at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    parser = config_parser()
    args = parser.parse_args()

    app = GUI(args)

    app.run()
