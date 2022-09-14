import keyboard_manager
import connection.btle_connection
import incoming_data_processor
import queue
import json


def read_configuration(config_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    return config


def main():

    incoming_data_queue = queue.Queue()
    connection_configuration = read_configuration('connection.json')
    robot_conn = connection.btle_connection.BTLEConnection(connection_configuration['BTLE']['address'],
                                                           connection_configuration['BTLE']['service_uuid'],
                                                           connection_configuration['BTLE']['char_uuid'],
                                                           incoming_data_queue)
    # robot_conn = connection.simulated_connection.SimConnection(incoming_data_queue)

    input_data_processor = incoming_data_processor.InputDataProcessor()

    # =============================================================================

    key_manager = keyboard_manager.KeyboardManager()

    # TODO with key_manager, input_data_processor, BTLE_comm...
    with robot_conn:
        key_manager.start()
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

            robot_conn.wait_for_notifications(0.001)
            try:
                data = incoming_data_queue.get_nowait()
                input_data_processor.process_incoming_data(data)
            except queue.Empty:
                pass

    # Should be stopped by now, but just in case
    key_manager.stop()
    # close csv file
    input_data_processor.close()

    print('Disconnected... Good Bye!')


if __name__ == '__main__':
    main()
