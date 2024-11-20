from datetime import datetime
import time

import gradio as gr
from llama_parse import LlamaParse
import os
import csv

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

    @staticmethod
    def process_string(original):
        parsed_document = None
        query = None

        if "||parsed_doc||" in original and "message||" in original:
            # Extract `query` between "message||" and the next "||"
            query_start = original.index("message||") + len("message||")
            query_end = original.index("||", query_start)
            query = original[query_start:query_end]

            # Extract `parsed_document` after "||parsed_doc||"
            parsed_doc_start = original.index("||parsed_doc||") + len("||parsed_doc||")
            parsed_document = original[parsed_doc_start:]

        elif "||parsed_doc||" in original:
            # Extract `parsed_document` after "||parsed_doc||"
            parsed_doc_start = original.index("||parsed_doc||") + len("||parsed_doc||")
            parsed_document = original[parsed_doc_start:]

        else : 
            query = original

        # Return results
        return query, parsed_document

    def print_like_dislike(self, x: gr.LikeData, req: gr.Request):

        if not os.path.exists(self.args.like_dislike_csv_path):
            with open(self.args.like_dislike_csv_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ip", "liked", "time", "query", "parsed_doc", "answer"])  #header row

        if x.index[0] % 2 == 1:  # if index odd, it's an ai response
            dump = []

            if req : 
                dump.append(req.client.host) #ip

            dump.append(x.liked) #liked
            dump.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) #time

            # for the query:
            # if it contains ||parsed_doc|| it means that a pdf was uploaded
            # 3 cases :
            # just message : ||parsed_doc|| absent => just fill query, parsed_doc is empty
            # just pdf : ||parsed_doc|| is there but there is no message|| => just fill parsed_doc
            # both : ||parsed_doc|| and  message|| are there => fill both

            query, parsed_doc = self.process_string(self.history[int(x.index[0]) - 1]["content"])

            dump.append(query)  # query
            if (parsed_doc):
                dump.append(parsed_doc.replace("\n", " "))  # parsed_doc
            else :
                dump.append(parsed_doc)

            dump.append("|".join(x.value[0].splitlines()[1:-1]))  # answer

            with open(self.args.like_dislike_csv_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(dump)

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

                else : 
                    self.history[-1]["content"] = query + "||parsed_doc||" + parsed_doc
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

                else : 
                    self.history[-1]["content"] = query + "||parsed_doc||" + parsed_doc
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
