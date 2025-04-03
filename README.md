# CP-Model-Zoo:  Natural Language Query System for Constraint Programming Models

## Introduction

Constraint Programming (CP) and its high-level modeling languages have long been recognized for their potential to achieve the holy grail of problem-solving stated by E. Freuder as "The user states the problem, the computer solves it". 
However, the complexity of CP modeling languages, the large number of global constraints available, and the art of creating good models have often hindered new non-expert users from choosing CP to solve their combinatorial problems.
While the ultimate dream is a tool that can generate an expert level model from a natural language description of a problem, the reality is that we are not yet there.

Recognizing this, we propose a simple intelligent tutoring system called **CP-Model-Zoo**, exploiting expert-written models accumulated through the solver competitions and the community efforts on CSPLib.
CP-Model-Zoo retrieves the closest source code model from a database of models, based on a user's natural language description of a combinatorial problem. 
This system, by design avoids hallucinations, ensuring that only expert-validated models are presented to the user.

## Installation Instructions

### Prerequisites

- Python 3.10 
- Git

### Step 1: Clone the Repository

```bash
git clone [your-repository-url]
cd LLM4CP
```

### Step 2: Set up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Setup

Create a `.env` file in the `app/assets/env/` directory with the following content:

```
GROQ_API_KEY=your-groq-api-key
```

## Running the Application

### GUI Interface

The application provides a Gradio-based GUI for searching constraint programming models:

```bash
python -m run_gui.py
```

This will launch a web interface where you can:
1. Enter queries about constraint programming problems
2. View matching MiniZinc models
3. Explore model source code

### Generating Vector Databases

Before using the search functionality, you need to generate the vector embeddings database:

```bash
python -m run_indexing.py
```

This process will:
1. Generate descriptions at different expertise levels (beginner, medium, expert)
2. Create vector embeddings databases for efficient searching

> [!TIP]  
> In this repo, we include both the raw data, as well as the embedding (vector) databases, making the app ready to run.
> In case one want to add additional models, or to update the existing ones, just drop the MiniZinc source code files in the `./data/input/merged_mzn_source_code` directory, and run the `run_indexing.py` script again.

### Command-Line Interface

You can also use the command-line interface for direct queries:

```bash
python -m run_inference.py
```

### Configuration Options

Key configuration options that can be specified in the config file or command line:

- `--mzn_path`: Directory containing MiniZinc model files
- `--txt_path`: Directory for generated text versions of models
- `--storage_dir`: Location for vector database storage
- `--output_dir`: Directory for generated outputs
- `--results_dir`: Directory for results
- `--descriptions_dir`: Directory for generated model descriptions

## Project Structure

- `app/`: Main application code
  - `data_processing/`: Code for processing MiniZinc models and creating vector databases
  - `gui/`: Gradio-based web interface
  - `inference/`: Query processing and model retrieval
  - `utils/`: Utility functions and constants
- `data/`: Data storage
  - `csplib_input/`: Input MiniZinc models
  - `vector_dbs/`: Generated vector databases
  - `output/`: Generated descriptions and other outputs
