from datetime import datetime
import gradio as gr
from llama_parse import LlamaParse
import os
import csv
import psycopg2

from app.inference.inference import Inference


# inspired by https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
global codes
codes = {}

global last_response
last_response = {}


class GUI:

    def __init__(self, args) -> None:
        self.args = args
        self.agent = Inference(args=self.args)
        self.parser = LlamaParse(
            result_type="markdown", api_key=self.args.llama_parse_key
        )
        self.histories = {} # {session_hash : [{message1},{message2}]}

        self.conn = psycopg2.connect(
            database = self.args.db_name,
            user = self.args.db_user,
            host = self.args.db_host,
            password = self.args.db_password,
            port = self.args.db_port,
        )
        self.cur = self.conn.cursor()

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS feedback(
            feedback_id SERIAL PRIMARY KEY,
            ip VARCHAR(15) NOT NULL,
            liked BOOLEAN NOT NULL,
            time TEXT NOT NULL,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            ranking TEXT NOT NULL);
            """
        )

        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS chat_history(
            message_id SERIAL PRIMARY KEY,
            session_hash TEXT NOT NULL,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            ranking TEXT NOT NULL,
            error BOOLEAN NOT NULL);
            """
        )

        self.conn.commit()

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

    def insert(self, table_name:str, columns:list, values:list):
        # TODO : retrieve the ranking
        try:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cur.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting into table {table_name}: {e}")
            self.conn.rollback()

    def like_dislike(self, x: gr.LikeData, req: gr.Request):

        if x.index[0] % 2 == 1:  # if index odd, it's an ai response
            dump = []

            if req:
                dump.append(req.client.host)  # ip

            dump.append(x.liked)  # liked
            dump.append(datetime.now().timestamp())  # time

            query = self.histories[req.session_hash][int(x.index[0]) - 1]["content"].replace("\n", " ").replace(";", ",")
            dump.append(query)  # query

            dump.append(x.value[0].replace("\n", " ").replace(";", ","))  # answer
            dump.append("ranking placeholder")

            self.insert("feedback", ["ip", "liked", "time", "query", "answer", "ranking"], dump)

    def add_message(self, message, request: gr.Request):

        inbool = request.session_hash in self.histories 

        if message["files"] is not None and message["text"] != "":
            for x in message["files"]:
                parsed_doc = self.parse_file(x)

                if not parsed_doc :
                    self.histories[request.session_hash].append(
                        {
                            "role": "assistant",
                            "content": "An error has occured during the parsing",
                        }
                    )

                content = (message["text"] + "\n" + parsed_doc)
                if inbool :
                    self.histories[request.session_hash].append(
                        {
                            "role": "user",
                            "content": content,
                        }
                    )
                else : 
                    self.histories[request.session_hash] = [{
                            "role": "user",
                            "content": content,
                        }]

                return self.histories[request.session_hash], gr.MultimodalTextbox(value=None, interactive=False)

        for x in message["files"]:
            parsed_doc = self.parse_file(x)

            if not parsed_doc :
                self.histories[request.session_hash].append(
                        {
                            "role": "assistant",
                            "content": "An error has occured during the parsing",
                        }
                    )

            if inbool :
                self.histories[request.session_hash].append({"role": "user", "content": parsed_doc})
            else : 
                self.histories[request.session_hash] = [{"role": "user", "content": parsed_doc}]

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

        if self.histories[request.session_hash][-1]["role"] == "assistant":
            return

        # Input
        query = self.histories[request.session_hash][-1]["content"]

        # Output
        response = self.agent.query_llm(question=query)

        answer = response.response

        for source_node in response.source_nodes:
            name = source_node.metadata["model_name"]
            source_code = source_node.metadata["source_code"]
            codes[name] = source_code

        # Print Output
        last_response["last"] = response
        self.histories[request.session_hash].append({"role": "assistant", "content": answer})
        return self.histories[request.session_hash]

    def update_buttons(self, request : gr.Request):
        if request.session_hash not in self.histories:
            return ["","","","",""]

        buttons_label = []

        for source_node in last_response["last"].source_nodes:
            score = source_node.score
            name = source_node.metadata["model_name"]
            buttons_label.append(f"{name} ({score:.3f})\n")

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
                        self.bot, [chatbot], [chatbot], api_name="bot_response"
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
