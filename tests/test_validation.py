from src.required.validation import validate_data
import json


def test_valid_input():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is True


def test_missing_field():
    data = {
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_id_too_long():
    data = {
        "id": "1"*101,
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_password_too_long():
    data = {
        "id": "1234",
        "password": "x"*101,
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_invalid_ip():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "1erw27.d0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_invalid_port():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "50504444444444444"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_negative_delay():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "-1",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_delay_too_large():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1000001",
            "steps": [
                "INCREASE 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_invalid_step():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "Add 5",
                "DECREASE 3"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_step_too_large():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 1000000000001"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is False


def test_decimal_step():
    data = {
        "id": "1234",
        "password": "verysafepassword1234",
        "server": {
            "ip": "127.0.0.1",
            "port": "5050"
        },
        "actions": {
            "delay": "1",
            "steps": [
                "INCREASE 5",
                "DECREASE 33.222222"
            ]
        }
    }

    assert validate_data(json.dumps(data)) is True
