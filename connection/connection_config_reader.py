import json


def read_connection_configuration(config_path):
    """
    Read Bluetooth Low Energy (BTLE) connection information from given config file in json format
    :param config_path: configuration file name
    :return: dictionary holding configuration data, None if file cannot be read 
    """
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
