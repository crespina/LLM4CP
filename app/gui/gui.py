import time

import gradio as gr
from llama_parse import LlamaParse
import json

from app.inference.inference import Inference


# inspired by https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks

class GUI:

    def __init__(self, args) -> None:
        self.args = args
        self.agent = Inference(args=self.args)
        self.parser = LlamaParse(result_type="markdown", api_key=self.args.llama_parse_key)
        self.history = []

    def parse_file(self, path):
        # FIXME: Didn't work, need to look into it.
        try :
            documents = self.parser.load_data(path)
            print("finished parsing")
            parsed_doc = ""
            for doc in documents:
                parsed_doc += doc.text
                parsed_doc += "\n"
            return parsed_doc
        except :
            print("An error has occured during the parsing")
            return None

    @staticmethod
    def split_message(input_str):
        parts = input_str.split("||")
        message = parts[1].strip()
        path = parts[3].strip()
        return message, path

    def print_like_dislike(self, x: gr.LikeData):
        dump = {}

        with open(self.args.like_dislike_json_path, "w") as outfile:
            json.dump(dictionary, outfile)

        print(x.index, x.value, x.liked)

    def add_message(self, message):
        if message["files"] is not None and message["text"] != '':
            for x in message["files"]:
                self.history.append({"role": "user", "content": "message||" + message["text"] + "||path||" + x})
                return self.history, gr.MultimodalTextbox(value=None, interactive=False)

        for x in message["files"]:
            self.history.append({"role": "user", "content": x})
        if message["text"] != '':
            self.history.append({"role": "user", "content": message["text"]})
        return self.history, gr.MultimodalTextbox(value=None, interactive=False)

    def bot(self, question):
        """
        Removed the `chatbot` parameter from the method signature, as it is not used.
        """

        # Input
        query = self.history[-1]["content"]
        error_message = None

        if query.endswith(".pdf"):

            if query.startswith("message||"):

                message, path = self.split_message(query)
                parsed_doc = self.parse_file(path)

                if parsed_doc == None:
                    error_message = "There has been an error while parsing the document, please try again in a few minutes."

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

                query = parsed_doc

        # Output

        if not error_message :

            response = self.agent.query_llm(question=query)

            answer = "The problem you are facing is probably : " + "\n"

            for source_node in response.source_nodes:
                score = source_node.score
                name = source_node.metadata["model_name"]
                # name = source_node.metadata["problem_family"]
                # TODO : also print the source code as an option
                source_code = source_node.metadata["source_code"]

                answer += str(name) + " with a score of " + str(score) + "\n"

            # Print Output
            self.history.append({"role": "assistant", "content": ""})

            for character in answer:
                self.history[-1]["content"] += character
                time.sleep(0.02)
                yield self.history

        else : 
            self.history.append({"role": "assistant", "content": ""})

            for character in error_message:
                self.history[-1]["content"] += character
                time.sleep(0.02)
                yield self.history

    def run(self):

        with gr.Blocks() as demo:
            chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, type="messages")

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

            bot_msg = chat_msg.then(self.bot, chatbot, chatbot, api_name="bot_response")
            bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

            chatbot.like(self.print_like_dislike, None, None, like_user_message=True)

        demo.launch(share=False)
