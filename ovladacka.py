import logging
import queue
import time
import keyboard_manager
from connection import btle_connection, connection_config_reader
from data_parsers import incoming_data_processor, packet_definition_reader
from data_writers import input_data_writer

logger = logging.getLogger(__name__)

CONFIG_FILE = 'connection.json'
PACKET_DEF_FILE = 'packet_definition.json'
NOTIFICATION_TIMEOUT = 0.001


def main():
    """Main entry point for the robot controller application"""
    incoming_data_queue = queue.Queue()

    # Load and validate configuration
    config = connection_config_reader.read_connection_configuration(CONFIG_FILE)
    if not config:
        logger.error('Cannot continue without connection configuration')
        return

    # Create robot connection
    try:
        btle_config = config['BTLE']
        robot_conn = btle_connection.BTLEConnection(
            btle_config['address'],
            btle_config['service_uuid'],
            btle_config['char_uuid'],
            incoming_data_queue
        )
    except KeyError as e:
        logger.error(f'Missing BTLE configuration key: {e}')
        return

    # Load packet definition
    packet_def = packet_definition_reader.read_packet_definition(PACKET_DEF_FILE)
    if not packet_def:
        logger.error('Cannot load packet definition')
        return

    # Create data processor and writer
    data_processor = incoming_data_processor.InputDataProcessor(packet_def)
    time_str = time.strftime("%Y-%m-%d-%H-%M-%S")
    data_writer = input_data_writer.InputDataWriter(
        packet_def,
        input_data_writer.prepare_output_folder(time_str),
        time_str
    )

    key_mgr = keyboard_manager.KeyboardManager()

    # Run main loop with context managers
    try:
        with robot_conn, key_mgr, data_writer:
            logger.info('Successfully connected to Robot via BLE')
            _main_loop(robot_conn, key_mgr, data_processor, data_writer, incoming_data_queue)
    except RuntimeError as e:
        logger.error(f'Connection error: {e}')
        return

    logger.info('Disconnected... Good Bye!')


def _main_loop(robot_conn, key_mgr, data_processor, data_writer, data_queue):
    """Main input/output loop for handling commands and incoming data"""
    while True:
        try:
            cmd = keyboard_manager.key_to_robot_command(key_mgr.get_key_nowait())
            if cmd:
                robot_conn.write(cmd)
        except keyboard_manager.TerminationRequested:
            break

        if robot_conn.wait_for_notifications(NOTIFICATION_TIMEOUT):
            data = data_queue.get_nowait()
            processed_data = data_processor.process_incoming_data(data)
            data_writer.write(processed_data)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
