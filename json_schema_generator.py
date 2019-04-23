import os
import sys
import json
from pathlib import Path
from src.cli_arguments import CliArguments, ArgumentNotFound
from src.json_schema_form import JsonSchemaForm


try:
    # parsing the CLI arguments
    cli_arguments = CliArguments(
        sys.argv[1:],
        mandatory_arguments=["input"],
        optional_arguments=["required-items", "invisible-items", "cast-types"]
    )
    # input JSON path detection and validation
    try:
        json_path = cli_arguments.get_argument_value("input")
    except ArgumentNotFound:
        raise Exception("JSON file path must be set as a first argument")
    if not os.path.isfile(json_path):
        raise Exception("Defined JSON file doesn't exist")
    # loading JSON file content
    json_string = Path(json_path).read_text()
    # generating the schema
    json_schema_form = JsonSchemaForm(
        json.loads(json_string),
        items_are_required=cli_arguments.is_argument_set("required-items"),
        items_are_invisible=cli_arguments.is_argument_set("invisible-items"),
        cast_types=cli_arguments.is_argument_set("cast-types")
    )
    # printing the schema on the standard output
    print(
        json.dumps(
            {
                "dataschema": json_schema_form.get_data_schema(),
                "uischema": json_schema_form.get_ui_schema()
            },
            indent=2
        )
    )
except Exception as e:
    print("Error: " + str(e))
