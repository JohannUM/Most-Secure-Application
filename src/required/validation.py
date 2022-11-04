from jsonschema import validate, ValidationError
import json

SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "maxLength": 100
        },
        "password": {
            "type": "string",
            "maxLength": 100
        },
        "server": {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "pattern": "^((25[0-5]|(2[0-4]|1\\d|[1-9]|)\\d)\.?\\b){4}$"
                },
                "port": {
                    "type": "string",
                    "pattern": "^(4915[0-1]|491[0-4]\\d|490\\d\\d|4[0-8]\\d{3}|[1-3]\\d{4}|[1-9]\\d{0,3}|0)$"
                }
            },
            "required": [
                "ip",
                "port"
            ]
        },
        "actions": {
            "type": "object",
            "properties": {
                "delay": {
                    "type": "string",
                    "pattern": "^([0-9]+)$"
                },
                "steps": {
                    "type": "array",
                    "items": [
                        {
                            "type": "string",
                            "pattern": "^((INCREASE|DECREASE) [-+]?([0-9]{1,3}[,]?)?([0-9]{3}[,]?)*[.]?[0-9]*)$"
                        }
                    ]
                }
            },
            "required": [
                "delay",
                "steps"
            ]
        }
    },
    "required": [
        "id",
        "password",
        "server",
        "actions"
    ]
}


def validate_data(json_str):

    try:
        json_data = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        print("INVALID INPUT: the json file does not follow the json structure.")
        return False

    try:
        validate(json_data, SCHEMA)
    except ValidationError as e:
        if e.validator == "required":
            print(f"INVALID INPUT: {e.message}.")
        else:
            print(f"INVALID INPUT: \'{e.instance}\' is an invalid argument for field {e.json_path}.")
        return False

    if int(json_data["actions"]["delay"]) > 1000000:
        return False

    for step in json_data["actions"]["steps"]:
        if float(step.split()[1])  > 1000000000000:
            return False

    return True
