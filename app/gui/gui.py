import os
import gradio as gr

from app.inference.inference import Inference


class GUI:

    def __init__(self, args) -> None:
        self.args = args
        self.agent = Inference(args=self.args)
        self.source_code_path = args.merged_mzn_source_path
        
        # Store the last retrieved nodes
        self.latest_nodes = []
        
        # Initial placeholder button labels
        self.placeholder_labels = [
            "Search results will appear here",
            "Click on a result to view its code",
            "Try searching for a constraint type",
            "You can search by problem name",
            "Or describe what you're looking for"
        ]

    def process_query(self, query):
        """Process the user query and return ranked results"""
        if not query.strip():
            # Return each button update separately, plus the markdown message
            return gr.update(visible=False, value=""), gr.update(visible=False, value=""), \
                   gr.update(visible=False, value=""), gr.update(visible=False, value=""), \
                   gr.update(visible=False, value=""), "Please enter a query."
            
        # Get response from inference
        nodes = self.agent.retrieve_nodes(question=query)
        
        # Store nodes for later use
        self.latest_nodes = nodes
        
        # Prepare button updates
        button_updates = []
        
        # Update buttons with results (up to 5)
        for i in range(5):
            if i < len(nodes):
                node = nodes[i]
                model_name = node.metadata.get("model_name", f"Unknown-{i}")
                score = node.score if hasattr(node, "score") else 0.0
                button_updates.append(gr.update(
                    value=f"{model_name} ({score:.3f})",
                    visible=True,
                    variant="primary"
                ))
            else:
                # Hide unused buttons
                button_updates.append(gr.update(visible=False, value=""))
        
        # Return each button update separately, plus the markdown message
        return button_updates[0], button_updates[1], button_updates[2], button_updates[3], button_updates[4], ""

    def display_source_code(self, btn_label):
        """Display the source code for the selected model"""
        if not btn_label:
            return "No model selected."
        
        # Don't respond to placeholder buttons
        if btn_label in self.placeholder_labels:
            return "Enter a query and click Search to find constraint programming models."
        
        # Extract model name from button label (remove score part)
        model_name = btn_label.split(" (")[0]
            
        # Find the file with the matching name
        file_path = os.path.join(self.source_code_path, f"{model_name}.txt")
        
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    source_code = f.read()
                return f"# {model_name}\n```minizinc\n{source_code}\n```"
            else:
                # Try to find a file that contains the model name (case insensitive)
                for filename in os.listdir(self.source_code_path):
                    if model_name.lower() in filename.lower():
                        with open(os.path.join(self.source_code_path, filename), "r") as f:
                            source_code = f.read()
                        return f"# {filename}\n```minizinc\n{source_code}\n```"
                
                # If still not found, check if there's a node with this name
                for node in self.latest_nodes:
                    if node.metadata.get("model_name") == model_name:
                        return f"# {model_name}\n```\n{node.text}\n```"
                        
                return f"Source code for {model_name} not found."
        except Exception as e:
            return f"Error loading source code: {str(e)}"

    def run(self):
        with gr.Blocks(title="CP Model Zoo") as webapp:
            with gr.Row():
                with gr.Column(scale=1):
                    # Welcome message
                    gr.Markdown("# CP Model Zoo\nSearch for constraint programming models")
                    
                    # Results container - will hold the buttons for ranked results
                    results_container = gr.Column()
                    with results_container:
                        gr.Markdown("### Search Results")
                        # Initialize buttons with placeholder texts
                        result_buttons = [
                            gr.Button(
                                self.placeholder_labels[i], 
                                visible=True,
                                variant="secondary"
                            ) for i in range(5)
                        ]
                    
                    # Query input at the bottom
                    query_input = gr.Textbox(
                        placeholder="Enter your query here...",
                        label="Query",
                        lines=3
                    )
                    submit_btn = gr.Button("Search", variant="primary")

                    # from app.utils.CONSTANTS import EXAMPLES
                    # _ = gr.Examples(EXAMPLES, query_input)
                    
                with gr.Column(scale=2):
                    # Source code display
                    code_display = gr.Markdown("Enter a query and click Search to find constraint programming models.")
            
            # Set up event handlers
            submit_btn.click(
                fn=self.process_query,
                inputs=query_input,
                outputs=[*result_buttons, code_display]
            )
            
            # Connect each button to the display function
            for btn in result_buttons:
                btn.click(
                    fn=self.display_source_code,
                    inputs=btn,
                    outputs=code_display
                )

        webapp.launch(share=True, inbrowser=True)
