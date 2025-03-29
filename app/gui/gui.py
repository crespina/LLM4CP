from datetime import datetime
import gradio as gr
from llama_index.llms.groq import Groq
from llama_parse import LlamaParse
import psycopg2
from llama_index.core import PromptTemplate

from app.inference.inference import Inference


# inspired by https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
# http://127.0.0.1:5050/browser/ the link for pgAdmin


class GUI:

    def __init__(self, args) -> None:
        self.args = args
        self.agent = Inference(args=self.args)

        self.describing_llm = Groq(
            model="llama3-70b-8192",
            api_key=args.groq_api_key,
            model_kwargs={"seed": 19851900},
            temperature=0.1,
        )
        self.prompt = PromptTemplate(
            "You are an expert in high-level constraint modelling and solving discrete optimization problems. \n"
            "Your task is to provide a short description of the following classical CP problem : {node1}."
        )

        self.parser = LlamaParse(
            result_type="markdown", api_key=self.args.llama_parse_key
        )

        self.conn = psycopg2.connect(
            database = self.args.db_name,
            user = self.args.db_user,
            host = self.args.db_host,
            password = self.args.db_password,
            port = self.args.db_port,
        )
        self.cur = self.conn.cursor()

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
        try:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cur.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting into table {table_name}: {e}")
            self.conn.rollback()

    def update(self, query, session_hash, values):
        columns = ["session_hash", "answer", "ranking1", "ranking2", "ranking3", "ranking4", "ranking5"]

        try:
            retrieve_id_sql = "SELECT message_id FROM chat_history WHERE query LIKE %s AND session_hash = %s;"
            query_splitted = query.split(".")[0] + '%'
            self.cur.execute(retrieve_id_sql, (query_splitted, session_hash,))
            id = self.cur.fetchone()

            set_clause = ", ".join([f"{column} = %s" for column in columns])
            query = f"""
            UPDATE chat_history
            SET {set_clause}
            WHERE message_id = %s;
            """
            values.append(id)

            self.cur.execute(query, values)
            self.conn.commit()

        except Exception as e:
            print(f"Error updating the chat history")
            return None

    def retrieve_history(self, session_hash):

        history = []
        try:
            query = """
            SELECT * 
            FROM chat_history
            WHERE session_hash = %s
            ORDER BY timestamp;
            """

            self.cur.execute(query, (session_hash,))

            rows = self.cur.fetchall()
            for row in rows : 
                history.append({"role": "user", "content": row[2]}) #add the query
                if (row[3]):
                    history.append({"role": "assistant", "content": row[3]}) #add the answer
            return history

        except Exception as e:
            print(f"Error retrieving rows for session_hash {session_hash}: {e}")
            return []

    def retrieve_ranking(self, answer, req:gr.Request):
        try:
            query = """
            SELECT ranking1, ranking2, ranking3, ranking4, ranking5
            FROM chat_history
            WHERE session_hash = %s AND answer LIKE E%s
            """

            self.cur.execute(query, (req.session_hash, answer,))

            row = self.cur.fetchone()
            return row

        except Exception as e:
            print(f"Error retrieving ranking {e}")
            return []

    def retrieve_query(self, answer, req:gr.Request):

        try:
            query = """
            SELECT query
            FROM chat_history
            WHERE session_hash = %s AND answer LIKE E%s
            """

            self.cur.execute(query, (req.session_hash, answer,))

            row = self.cur.fetchone()
            return row[0]

        except Exception as e:
            print(f"Error retrieving ranking {e}")
            return []

    def like_dislike(self, x: gr.LikeData, req: gr.Request):

        if x.index[0] % 2 == 1:  # if index odd, it's an ai response
            answer = x.value[0]
            sesh = req.session_hash  
            try:
                query = f"""
                UPDATE chat_history
                SET liked = %s
                WHERE answer LIKE E%s AND session_hash = %s;
                """

                self.cur.execute(query, (x.liked, answer, sesh,))
                self.conn.commit()

            except Exception as e:
                print(f"Error updating the chat history")
                return None

    def add_message(self, message, request: gr.Request):
        table_name = "chat_history"
        columns = ["ip", "session_hash", "query", "error", "timestamp"]
        ip = request.client.host
        session_hash = request.session_hash

        if message["files"] is not None and message["text"] != "":
            for x in message["files"]:
                parsed_doc = self.parse_file(x)

                if not parsed_doc :
                    self.insert(table_name=table_name, columns=columns, values=[ip, session_hash, "Unknown document : An error has occured during the parsing of your document, please try again.", True, datetime.now()])

                    history = self.retrieve_history(session_hash)
                    return history, gr.MultimodalTextbox(value=None, interactive=False)

                query = (message["text"] + "\n" + parsed_doc)
                self.insert(table_name=table_name, columns=columns, values=[ip, session_hash, query, False, datetime.now()])

                history = self.retrieve_history(session_hash)
                return history, gr.MultimodalTextbox(value=None, interactive=False)

        for x in message["files"]:
            parsed_doc = self.parse_file(x)

            if not parsed_doc :
                self.insert(table_name=table_name, columns=columns, values=[ip, session_hash, "Unknown document : An error has occured during the parsing of your document, please try again.", True, datetime.now()])
                history = self.retrieve_history(session_hash)
                return history, gr.MultimodalTextbox(value=None, interactive=False)

            self.insert(table_name=table_name, columns=columns, values=[ip, session_hash, parsed_doc, False, datetime.now()])
            history = self.retrieve_history(session_hash)
            return history, gr.MultimodalTextbox(value=None, interactive=False)

        if message["text"] != "":
            self.insert(table_name=table_name, columns=columns, values=[ip, session_hash, message["text"], False, datetime.now()])
            history = self.retrieve_history(session_hash)
            return history, gr.MultimodalTextbox(value=None, interactive=False)

        else : 
            print("error")
            return

    def bot(self, question, request : gr.Request):

        values = [request.session_hash]
        query = question[-1]["content"]

        # Output
        response = self.agent.query_llm(question=query)
        values.append(response.response)

        for source_node in response.source_nodes:
            name = source_node.metadata["model_name"]
            score = source_node.score
            values.append(f"{name} ({score:.3f})\n")

        descr_prompt = self.prompt.format(node1=values[2][0:-8])
        description = self.describing_llm.complete(prompt=descr_prompt)
        description_text = description.text
        values[1] = description_text
        # response.response = description_text
        # Print Output
        self.update(query, request.session_hash, values)
        question.append({"role": "assistant", "content": description_text})

        return question

    def update_buttons(self, chat_history, req:gr.Request):
        if not chat_history :
            return ["","","","",""]

        ranking = self.retrieve_ranking(chat_history[-1]["content"], req)

        return ranking

    def show_code(self, selected_val):
        try : 
            query = """
                SELECT model_code
                FROM source_codes
                WHERE model_name LIKE E%s 
                """
            self.cur.execute(query, (selected_val.split()[0],))

            row = self.cur.fetchone()
            return row[0]
        except Exception as e:
            print(f"Error retrieving code {e}")
            return []

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
                    def update_buttons_ui(chat_history, req:gr.Request):
                        labels = self.update_buttons(chat_history, req)
                        updates = [
                            gr.update(value=label, visible=True) for label in labels
                        ]
                        return updates

                    bot_msg.then(update_buttons_ui, chatbot, buttons)

                    # Link each button to its explanation
                    for button in buttons:
                        button.click(self.show_code, inputs=button, outputs=explanation)

                    chatbot.like(self.like_dislike, None, None, like_user_message=True)

                with gr.Column(scale=1):
                    for button in buttons:
                        button.render()
                    explanation.render()

        app.launch(share=True, inbrowser=True)
