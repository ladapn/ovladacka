import keyboard_manager
import connection.btle_connection
import incoming_data_processor
import input_data_writer
import queue
import json


def read_configuration(config_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    return config


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


def main():

    incoming_data_queue = queue.Queue()
    connection_configuration = read_configuration('connection.json')
    robot_conn = connection.btle_connection.BTLEConnection(connection_configuration['BTLE']['address'],
                                                           connection_configuration['BTLE']['service_uuid'],
                                                           connection_configuration['BTLE']['char_uuid'],
                                                           incoming_data_queue)
    # robot_conn = connection.simulated_connection.SimConnection(incoming_data_queue)

    packet_definition = read_packet_definition('packet_definition.json')
    input_data_processor = incoming_data_processor.InputDataProcessor(packet_definition)

    in_data_writer = input_data_writer.InputDataWriter(packet_definition)

    # =============================================================================

    key_manager = keyboard_manager.KeyboardManager()

    # TODO with key_manager, input_data_processor, BTLE_comm...
    with robot_conn, key_manager:
        while True:

            try:
                key = key_manager.get_key_nowait()
                if key:
                    cmd = keyboard_manager.key_translator(key)
                    if cmd:
                        print(cmd)
                        robot_conn.write(cmd)
            except keyboard_manager.KeyboardManagerEnded:
                break

            if robot_conn.wait_for_notifications(0.001):
                data = incoming_data_queue.get_nowait()
                processed_data = input_data_processor.process_incoming_data(data)
                in_data_writer.write(processed_data)

    # close csv file
    in_data_writer.close()

    print('Disconnected... Good Bye!')


if __name__ == '__main__':
    main()
