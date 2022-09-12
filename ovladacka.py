import keyboard_manager
import connection.btle_connection
import packet_writer
import packet_parser
import queue


class PacketProcessor:
    def __init__(self, parser, writer, packet_len):
        self.parser = parser
        self.writer = writer
        self.packet_len = packet_len


class InputDataProcessor:
    def __init__(self):
        self.leftovers = None

        self.packet_processors = {80: PacketProcessor(parser=packet_parser.StatusPacketParser(),
                                                      writer=packet_writer.StatusPacketWriter(),
                                                      packet_len=16)}

        # TODO -> put all these related classes to one module: packet_data_manager or input_data_processor
        usnd_packet_ids = [100, 101, 102, 103]
        usnd_processor = PacketProcessor(parser=packet_parser.UsndPacketParser(),
                                         writer=packet_writer.USNDPacketWriter(usnd_packet_ids),
                                         packet_len=10)

        for packet_id in usnd_packet_ids:
            self.packet_processors[packet_id] = usnd_processor

    def close(self):
        for processor in self.packet_processors.values():
            processor.writer.close()

    @staticmethod
    def process_packet(packet_id, packet, packet_processor):
        packet_data = packet_processor.parser.parse_raw_data(packet_id, packet)
        print(packet_data)
        packet_processor.writer.write_packet(packet_id, packet_data)

    def process_incoming_data(self, data):
        print("data received")
        print(data)

        # get byte, check ID, if known id, get its length
        # knowing length, check CRC -> if ok, packet ok -> extract;
        # if not, go back to ID crawling

        # This is to handle data split into multiple data bursts
        if self.leftovers:
            # put the leftover of previous data burst in front of the current one
            data = self.leftovers + data
            self.leftovers = None

        idx = 0
        while idx < len(data):
            packet_id = data[idx]
            if packet_id in self.packet_processors:
                packet_processor = self.packet_processors[packet_id]
                packet = data[idx: idx + packet_processor.packet_len]

                # Is the packet contained in this data, or does it continue in the next burst?
                if idx + packet_processor.packet_len > len(data):
                    self.leftovers = data[idx:]
                    break

                try:
                    InputDataProcessor.process_packet(packet_id, packet, packet_processor)
                except packet_parser.ParserBadChecksum:
                    print(f'Broken checksum found, Packet ID: {packet_id}')
                except packet_parser.ParserException as ex:
                    print(f'something bad has happened while processing data of packet ID {packet_id}: {ex}')

                idx = idx + packet_processor.packet_len - 1

            idx = idx + 1


def main():

    address = '00:13:AA:00:12:27'
    service_uuid = '0000ffe0-0000-1000-8000-00805f9b34fb'
    char_uuid = '0000ffe1-0000-1000-8000-00805f9b34fb'

    incoming_data_queue = queue.Queue()
    robot_conn = connection.btle_connection.BTLEConnection(address, service_uuid, char_uuid, incoming_data_queue)
    # robot_conn = connection.simulated_connection.SimConnection(incoming_data_queue)

    input_data_processor = InputDataProcessor()

    # =============================================================================

    key_manager = keyboard_manager.KeyboardManager()
    key_manager.start()

    # TODO with key_manager, input_data_processor, BTLE_comm...
    with robot_conn:
        print(f'Connected Successfully to {address}')
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
