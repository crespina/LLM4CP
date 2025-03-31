import psycopg2
from configuration import config_parser
import os

corresp = {
    "All-Interval_Series": "all_interval",
    "Balanced_Academic_Curriculum_Problem__BACP_": "curriculum",
    "Balanced_Incomplete_Block_Designs": "bibd",
    "Bus_Driver_Scheduling": "bus_scheduling_csplib",
    "Car_Sequencing": "car",
    "Crossfigures": "crossfigure",
    "Diamond-free_Degree_Sequences": "diamond_free_degree_sequence",
    "Golomb_rulers": "golomb",
    "Graceful_Graphs": "graph",
    "Killer_Sudoku": "killer_sudoku",
    "Langford_s_number_problem": "langford",
    "Magic_Hexagon": "magic_hexagon",
    "Magic_Squares_and_Sequences": "magic_sequence",
    "Maximum_Clique": "clique",
    "Maximum_density_still_life": "maximum_density_still_life",
    "N-Queens": "queens",
    "Nonogram": "nonogram_create_automaton2",
    "Number_Partitioning": "partition",
    "Optimal_Financial_Portfolio_Design": "opd",
    "Quasigroup_Completion": "QuasigroupCompletion",
    "Quasigroup_Existence": "QuasiGroupExistence",
    "Rotating_Rostering_Problem": "RosteringProblem",
    "Schur_s_Lemma": "schur",
    "Social_Golfers_Problem": "golfers",
    "Solitaire_Battleships": "sb",
    "Steiner_triple_systems": "steiner",
    "Stochastic_Assignment_and_Scheduling_Problem": "stoch_fjsp",
    "Synchronous_Optical_Networking__SONET__Problem": "sonet_problem",
    "Template_Design": "template_design",
    "The_n-Fractions_Puzzle": "fractions",
    "The_Rehearsal_Problem": "rehearsal",
    "Traffic_Lights": "traffic_lights_table",
    "Traveling_Tournament_Problem_with_Predefined_Venues__TTPPV_": "TTPPV",
    "Vessel_Loading": "vessel-loading",
    "Warehouse_Location_Problem": "warehouses",
    "Water_Bucket_Problem": "water_buckets1",
}

parser = config_parser()
args = parser.parse_args()
conn = psycopg2.connect(
            database = args.db_name,
            user = args.db_user,
            host = args.db_host,
            password = args.db_password,
            port = args.db_port,
        )

cur = conn.cursor()

descr_folder = args.descriptions_folder


def create_tables(cur, conn):
    """Creates the necessary tables if they do not already exist."""

    # SQL statements to create tables if they don't exist
    create_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS source_codes (
            model_id SERIAL PRIMARY KEY,
            model_name TEXT NOT NULL,
            model_family TEXT NOT NULL,
            model_code TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id SERIAL PRIMARY KEY,
            ip TEXT NOT NULL,
            liked BOOLEAN NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            ranking INTEGER
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            message_id SERIAL PRIMARY KEY,
            session_hash TEXT NOT NULL,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            error TEXT,
            ranking1 INTEGER,
            ranking2 INTEGER,
            ranking3 INTEGER,
            ranking4 INTEGER,
            ranking5 INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            liked BOOLEAN,
            ip TEXT
        );
        """,
    ]

    # Execute each table creation query
    for query in create_table_queries:
        cur.execute(query)

    # Commit and close connection
    conn.commit()

    print("Tables are created or already exist.")


def populate_source_codes(folder_path, corresp, cur, conn):
    """Fills the source_codes table with data from source_code.txt files."""
    
    # Iterate over subfolders (each representing a problem)
    for model_id, model_name in enumerate(os.listdir(folder_path), start=1):
        model_folder = os.path.join(folder_path, model_name)
        source_code_path = os.path.join(model_folder, "source_code.txt")

        # Ensure it's a directory and the file exists
        if os.path.isdir(model_folder) and os.path.isfile(source_code_path):
            with open(source_code_path, "r", encoding="utf-8") as f:
                model_code = f.read()

            # Determine model family from corresp dictionary
            model_family = next(
                (fam for fam, name in corresp.items() if name == model_name), "Unknown"
            )

            # Insert into the database
            cur.execute(
                """
                INSERT INTO source_codes (model_name, model_family, model_code)
                VALUES (%s, %s, %s);
                """,
                (model_name, model_family, model_code),
            )

    # Commit and close connection
    conn.commit()


def print_content(cur,conn):
    # Get all table names from the public schema
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"\n=== Table: {table_name} ===")

        # Fetch all rows from the table
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        # Fetch column names
        col_names = [desc[0] for desc in cur.description]

        # Print column names and rows
        print(f"Columns: {col_names}")
        for row in rows:
            print(row)
            print("")


# Call the function
create_tables(cur, conn)
populate_source_codes(descr_folder,corresp,cur,conn)
print_content(cur, conn)

cur.close()
conn.close()
