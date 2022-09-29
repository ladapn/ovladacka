import json


def read_connection_configuration(config_path):
    config = None

    try:
        config_file = open(config_path, 'r')
    except FileNotFoundError:
        print('Connection configuration file "connection.json" was not found. Please create "connection.json" based on'
              ' provided template "connection.json.TEMPLATE"')
    else:
        with config_file:
            config = json.load(config_file)

    return config
