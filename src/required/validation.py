from schema import Schema, Use, SchemaError
import json
import re
import ipaddress


SCHEMA = Schema({
    'id': str,
    'password': str,
    'server': {
        'ip': str,
        'port': Use(int),
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
    except json.decoder.JSONDecodeError:
        return False

    # check if json_dict follows SCHEMA
    if check(SCHEMA, json_dict) is False:
        return False

    # check if [ip] is in correct format
    try:
        ipaddress.ip_address(json_dict['server']['ip'])
    except ValueError:
        return False

    # check if [port] is in correct format
    if 1 <= int(json_dict['server']['port']) <= 65535:
        pass
    else:
        return False

    # check if [steps] are in correct format
    for step in json_dict['actions']['steps']:
        try:
            if re.compile('INCREASE \\d').match(step) is None and re.compile('DECREASE \\d').match(step) is None:
                return False
        except TypeError:
            return False

    return True
