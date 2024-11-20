import os
from langchain.output_parsers import ResponseSchema
from tqdm import tqdm
import csv
import json

families = {
    "assign": ["assign", "assign_dual", "assign_inverse"],
    "aust_color": ["aust_color", "aust_colord"],
    "buggy": [
        "context",
        "debug1",
        "debug2",
        "debug3",
        "division",
        "evenproblem",
        "missing_solution",
        "test",
        "trace",
    ],
    "carpet_cutting": ["carpet_cutting", "carpet_cutting_geost", "cc_geost"],
    "cell_block": ["cell_block", "cell_block_func"],
    "cluster": ["cluster"],
    "compatible_assignment": ["compatible_assignment", "compatible_assignment_opt"],
    "constrained_connected": ["constrained_connected"],
    "crazy_sets": ["crazy_sets", "crazy_sets_global"],
    "doublechannel": ["doublechannel"],
    "flattening": [
        "flattening0",
        "flattening1",
        "flattening2",
        "flattening3",
        "flattening4",
        "flattening5",
        "flattening6",
        "flattening7",
        "flattening8",
        "flattening9",
        "flattening10",
        "flattening11",
        "flattening12",
        "flattening13",
        "flattening14",
    ],
    "jobshop": ["jobshop", "jobshop2", "jobshop3"],
    "knapsack": [
        "knapsack",
        "knapsack01",
        "knapsack01bool",
        "knapsack01set",
        "knapsack01set_concise",
    ],
    "langford": ["combinedlangford", "inverselangford", "langford"],
    "linetsp": ["ltsp"],
    "loan": ["loan1", "loan2"],
    "mip": ["mip1", "mip2", "mip3", "mip4", "mip5"],
    "nurses": ["nurses", "nurses_let"],
    "photo": ["photo"],
    "production_planning": ["simple-prod-planning"],
    "project_scheduling": ["project_scheduling", "project_scheduling_nonoverlap"],
    "rcpsp": ["rcpsp"],
    "rel_sem": ["rel_sem", "rel_sem2"],
    "restart": ["restart", "restart2", "restarta"],
    "search": ["assign", "domwdeg"],
    "setselect": [
        "setselect",
        "setselectr",
        "setselectr2",
        "setselectr3",
        "setselect2",
        "setselect3",
    ],
    "shipping": ["shipping"],
    "stable_roommates": ["stableroommates", "stable_roommates_func"],
    "submultisetsum": ["submultisetsum"],
    "table_seating": ["table_seating", "table_seating_gcc"],
    "team_select": ["teamselect", "teamselect_advanced"],
    "array_quest": ["array_quest"],
    "graph": ["graph"],
    "itemset_mining": ["itemset_mining"],
    "lots": ["lots"],
    "missingsolution": ["missingsolution"],
    "myabs": ["myabs"],
    "mydiv": ["mydiv"],
    "queens": ["queens"],
    "square_pack": ["square_pack"],
    "table_example": ["table_example"],
    "toomany": ["toomany"],
    "toy_problem": ["toy_problem"],
}

def convert_mzn_to_txt(mzn_path, txt_path):
    for dir_path, _, filenames in os.walk(mzn_path):
        for filename in tqdm(filenames, desc="Converting .mzn to .txt"):
            if filename.endswith(".mzn"):
                mzn_file_path = os.path.join(dir_path, filename)
                with open(mzn_file_path, 'r') as mzn_file:
                    content = mzn_file.read()

                relative_path = os.path.relpath(dir_path, mzn_path)
                output_dir_path = os.path.join(txt_path, relative_path)

                os.makedirs(output_dir_path, exist_ok=True)

                txt_file_path = os.path.join(output_dir_path, filename.replace('.mzn', '.txt'))

                with open(txt_file_path, 'w') as txt_file:
                    txt_file.write(content)


def get_response_schema(query_config_dict):
    response_schema = []
    for field, description in query_config_dict.items():
        response_schema.append(ResponseSchema(name=field.strip(), description=description.strip()))
    return response_schema

def problem_family(problem_name):
    # Given the name of the problem, returns its family

    for family_name, problems in families.items():
        for problem in problems:
            if problem == problem_name:
                problem_name = problem_name.replace(problem, family_name)

    return problem_name

def transform_csv_into_json(csv_path, json_path):
    data = []
    with open(csv_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(row)

    # Write the data to a JSON file
    with open(json_path, "w") as json_file:
        json.dump(data, json_file)
