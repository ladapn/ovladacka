import json


def read_packet_definition(definition_file_name):
    """
    Read from a json file definition of packets coming from robot
    :param definition_file_name: filename of the configuration file
    :return: dictionary with packet id as a key - this dictionary holds another dictionary containing packet definitions
    """
    with open(definition_file_name, 'r') as definition_file:
        definitions = json.load(definition_file)

    # TODO: perform input validity checks
    id_to_packet_info = {}
    for d in definitions:
        if not isinstance(d['id'], list):
            ids = [d['id']]
        else:
            ids = d['id']

        for packet_id in ids:
            id_to_packet_info[packet_id] = {key: d[key] for key in d if key != 'id'}

    return id_to_packet_info
