from schema import Schema, And, Use, Optional, SchemaError
import json
import re

SCHEMA = Schema({
    'id': str,
    'password': str,
    'server': {
        'ip': str,
        'port': And(Use(str)),
    },
    'actions': {
        'delay': Use(int),
        'steps': list
    }
})


def check(conf_schema, conf):
    try:
        conf_schema.validate(conf)
        return True
    except SchemaError:
        return False


def validate(json_str):

    # check if json_str can be converted to dictionary data type
    try:
        json_dict = json.loads(json_str)
        print(json_dict)
    except json.decoder.JSONDecodeError:
        return False

    # check if json_dict follows SCHEMA
    if check(SCHEMA, json_dict) is False:
        return False

    # check if [ip] and [port] is in correct format
    if re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}').match(json_dict['server']['ip']) is None:
        return False
    if re.compile('\d{4}').match(json_dict['server']['port']) is None:
        return False

    # check if [steps] are in correct format
    for step in json_dict['actions']['steps']:
        try:
            if re.compile('INCREASE \d').match(step) is None and re.compile('DECREASE \d').match(step) is None:
                return False
        except TypeError:
            return False

    return True
    

    



