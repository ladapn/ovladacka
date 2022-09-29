import json


def read_packet_definition(definition_path):
    with open(definition_path, 'r') as definition_file:
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
