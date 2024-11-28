from datetime import datetime
import time

import openai
import gradio as gr
from llama_parse import LlamaParse
import os
import csv

from app.inference.inference import Inference


# inspired by https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
global codes
codes = {}


class GUI:

    def __init__(self, args) -> None:
        self.args = args
        self.agent = Inference(args=self.args)
        self.parser = LlamaParse(
            result_type="markdown", api_key=self.args.llama_parse_key
        )
        self.histories = {} # {session_hash : [{message1},{message2}]}
        self.client = openai.OpenAI(api_key=self.args.openai_api_key)
        self.threads = {}
        # TODO: when uploading the PDF, do not print out the path of it, just its content.

    def parse_file(self, path):
        try:
            documents = self.parser.load_data(path)
            print("finished parsing")
            parsed_doc = ""
            for doc in documents:
                parsed_doc += doc.text
                parsed_doc += "\n"
            return parsed_doc
        except:
            print("An error has occured during the parsing")
            return None

    @staticmethod
    def split_message(input_str):
        parts = input_str.split("||")
        message = parts[1].strip()
        path = parts[3].strip()
        return message, path

    @staticmethod
    def process_string(original):
        parsed_document = None
        query = None

        if "||parsed_doc||" in original and "message||" in original:

            query_start = original.index("message||") + len("message||")
            query_end = original.index("||", query_start)
            query = original[query_start:query_end]

            parsed_doc_start = original.index("||parsed_doc||") + len("||parsed_doc||")
            parsed_document = original[parsed_doc_start:]

        elif "||parsed_doc||" in original:
            parsed_doc_start = original.index("||parsed_doc||") + len("||parsed_doc||")
            parsed_document = original[parsed_doc_start:]

        else:
            query = original

        return query, parsed_document

    def like_dislike(self, x: gr.LikeData, req: gr.Request):
        _template_path = "./data/output"  # TODO : change this into args.output_path
        if not os.path.exists(_template_path):
            os.makedirs(_template_path)

        if not os.path.exists(self.args.like_dislike_csv_path):
            with open(self.args.like_dislike_csv_path, "a", newline="") as file:
                # TODO: make it into a DB
                # [ip*, timestamp, liked, query*, parsed_doc, answer]
                # * primary keys
                # if entry is duplicate, update with the newest one based on timestamp.
                writer = csv.writer(file)
                writer.writerow(
                    ["ip", "liked", "time", "query", "parsed_doc", "answer"]
                )  # header row

        if x.index[0] % 2 == 1:  # if index odd, it's an ai response
            dump = []

            if req:
                dump.append(req.client.host)  # ip

            dump.append(x.liked)  # liked
            dump.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))  # time

            query, parsed_doc = self.process_string(
                self.histories[req.session_hash][int(x.index[0]) - 1]["content"]
            )

            dump.append(query)  # query
            if parsed_doc:
                dump.append(parsed_doc.replace("\n", " "))  # parsed_doc
            else:
                dump.append(parsed_doc)  # parsed_doc = None

            dump.append("|".join(x.value[0].splitlines()[1:-1]))  # answer

            with open(self.args.like_dislike_csv_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(dump)

    def add_message(self, message, request: gr.Request):

        inbool = request.session_hash in self.histories 

        if message["files"] is not None and message["text"] != "":
            for x in message["files"]:
                if inbool :
                    self.histories[request.session_hash].append(
                        {
                            "role": "user",
                            "content": "message||" + message["text"] + "||path||" + x,
                        }
                    )
                else : 
                    self.histories[request.session_hash] = [{
                            "role": "user",
                            "content": "message||" + message["text"] + "||path||" + x,
                        }]

                return self.histories[request.session_hash], gr.MultimodalTextbox(value=None, interactive=False)

        for x in message["files"]:
            if inbool :
                self.histories[request.session_hash].append({"role": "user", "content": x})
            else : 
                self.histories[request.session_hash] = [{"role": "user", "content": x}]

        if message["text"] != "":
            if inbool :
                self.histories[request.session_hash].append(
                    {"role": "user", "content": message["text"]}
                )
            else :
                self.histories[request.session_hash] = [
                    {"role": "user", "content": message["text"]}
                ]

        return self.histories[request.session_hash], gr.MultimodalTextbox(value=None, interactive=False)

    def bot(self, question, request : gr.Request):

        # Input
        query = self.histories[request.session_hash][-1]["content"]
        error_message = None

        if query.endswith(".pdf"):

            if query.startswith("message||"):

                message, path = self.split_message(query)
                parsed_doc = self.parse_file(path)

                if parsed_doc == None:
                    error_message = "There has been an error while parsing the document, please try again in a few minutes."

                else:
                    self.histories[request.session_hash][-1]["content"] = query + "||parsed_doc||" + parsed_doc
                    query = (
                        "here is the user's question"
                        + "\n"
                        + message
                        + "\n"
                        + "and here is the document"
                        + "\n"
                        + parsed_doc
                    )

            else:
                parsed_doc = self.parse_file(query)

                if parsed_doc == None:
                    error_message = "There has been an error while parsing the document, please try again in a few minutes."

                else:
                    self.histories[request.session_hash][-1]["content"] = query + "||parsed_doc||" + parsed_doc
                    query = parsed_doc

        # Output

        if not error_message:

            response = self.agent.query_llm(question=query)

            answer = "The problem you are facing is probably : " + "\n"

            for source_node in response.source_nodes:
                score = source_node.score
                name = source_node.metadata["model_name"]
                # name = source_node.metadata["problem_family"]
                source_code = source_node.metadata["source_code"]
                codes[name] = source_code

                answer += f"{name} ({score:.3f})\n"

            # Print Output
            self.histories[request.session_hash].append({"role": "assistant", "content": answer})
            return self.histories[request.session_hash]

            """
            # TODO: Stop streaming the answer, just print it all at once
            for character in answer:
                self.history[-1]["content"] += character
                time.sleep(0.02)
                yield self.history
            """

        else:
            self.histories[request.session_hash].append({"role": "assistant", "content": error_message})
            return self.histories[request.session_hash]
            """
            # TODO: Stop streaming the answer, just print it all at once
            for character in error_message:
                self.history[-1]["content"] += character
                time.sleep(0.02)
                yield self.history
            """

    def update_buttons(self, request : gr.Request):
        if request.session_hash not in self.histories:
            return ["","","","",""]
        bot_response = self.histories[request.session_hash][-1]["content"]

        buttons_label = []

        for model in bot_response.splitlines()[1:]:
            buttons_label.append(model)

        return buttons_label

    def show_code(self, selected_val):
        return codes[selected_val.split()[0]]

    def run(self):

        buttons = [gr.Button("", visible=False) for _ in range(5)]

        explanation = gr.Markdown(
            "Click on a value in the Dataframe to see more details here."
        )

        with gr.Blocks() as app:

            with gr.Row():

                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        elem_id="chatbot", bubble_full_width=False, type="messages"
                    )

                    chat_input = gr.MultimodalTextbox(
                        interactive=True,
                        file_count="multiple",
                        placeholder="Enter message or upload file...",
                        show_label=False,
                        file_types=[".pdf"],
                    )

                    chat_msg = chat_input.submit(
                        self.add_message, [chat_input], [chatbot, chat_input]
                    )

                    bot_msg = chat_msg.then(
                        self.bot, chatbot, chatbot, api_name="bot_response"
                    )
                    bot_msg.then(
                        lambda: gr.MultimodalTextbox(interactive=True),
                        None,
                        [chat_input],
                    )

                    # Dynamically update button labels
                    def update_buttons_ui(request : gr.Request):
                        labels = self.update_buttons(request)
                        updates = [
                            gr.update(value=label, visible=True) for label in labels
                        ]
                        return updates

                    bot_msg.then(update_buttons_ui, None, buttons)

                    # Link each button to its explanation
                    for button in buttons:
                        button.click(self.show_code, inputs=button, outputs=explanation)

                    chatbot.like(self.like_dislike, None, None, like_user_message=True)

                with gr.Column(scale=1):
                    for button in buttons:
                        button.render()
                    explanation.render()

        app.launch(share=True, inbrowser=True)
