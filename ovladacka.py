import keyboard_manager
from connection import btle_connection
from data_parsers import incoming_data_processor,  packet_definition_reader
from data_writers import input_data_writer
import queue
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


def main():

    incoming_data_queue = queue.Queue()
    connection_configuration = read_connection_configuration('connection.json')

    if not connection_configuration:
        print('Cannot continue without connection configuration, exiting...')
        return

    robot_conn = btle_connection.BTLEConnection(connection_configuration['BTLE']['address'],
                                                connection_configuration['BTLE']['service_uuid'],
                                                connection_configuration['BTLE']['char_uuid'],
                                                incoming_data_queue)
    # robot_conn = connection.simulated_connection.SimConnection(incoming_data_queue)

    if not robot_conn.connect():
        print('Cannot connect to robot, exiting...')
        return

    packet_definition = packet_definition_reader.read_packet_definition('packet_definition.json')
    input_data_processor = incoming_data_processor.InputDataProcessor(packet_definition)

    in_data_writer = input_data_writer.InputDataWriter(packet_definition, input_data_writer.prepare_output_folder())

    key_manager = keyboard_manager.KeyboardManager()

    with robot_conn, key_manager, in_data_writer:
        while True:
            try:
                cmd = keyboard_manager.key_to_robot_command(key_manager.get_key_nowait())
                if cmd:
                    robot_conn.write(cmd)
            except keyboard_manager.TerminationRequested:
                break

            if robot_conn.wait_for_notifications(0.001):
                data = incoming_data_queue.get_nowait()
                processed_data = input_data_processor.process_incoming_data(data)
                in_data_writer.write(processed_data)

    print('Disconnected... Good Bye!')


if __name__ == '__main__':
    main()
