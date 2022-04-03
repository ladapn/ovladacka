from bluepy import btle
import keyboard_manager
import packet_writer
import packet_parser
# import queue


class RobotCommDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.pkt_processor = InputDataProcessor()

    def handleNotification(self, cHandle, data):
        self.pkt_processor.process_incoming_data(data)
        # TODO: put data to a queue
        # self.incoming_data_queue.add(data) -> a to bude vse, co tu bude


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
    service_uuid = btle.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')
    char_uuid = btle.UUID('0000ffe1-0000-1000-8000-00805f9b34fb')

    print(f'Attempting to connect to {address}')

    p = None

    number_of_retries = 3
    for tries in range(number_of_retries):
        try:
            p = btle.Peripheral(address)
            break
        except btle.BTLEDisconnectError as e:
            print(e)
            if tries == (number_of_retries - 1):
                print('Giving up')
                exit()
            print('Trying again...')

    print('Connected Successfully')

    my_delegate = RobotCommDelegate()
    p.setDelegate(my_delegate)

    svc = p.getServiceByUUID(service_uuid)
    ch = svc.getCharacteristics(char_uuid)[0]

    # Enable notifications for the characteristics
    # Without this nothing happens when device sends data to PC...
    p.writeCharacteristic(ch.valHandle + 1, b"\x01\x00")
    #
    # =============================================================================

    key_manager = keyboard_manager.KeyboardManager()
    key_manager.start()

    while True:

        try:
            key = key_manager.get_key_nowait()
            if key:
                cmd = keyboard_manager.key_translator(key)
                if cmd:
                    print(cmd)
                    ch.write(cmd)

            # TODO zkontroluj frontu prichozich dat -> zavolej paket parser
        except keyboard_manager.KeyboardManagerEnded:
            break

        # TODO: reconnect when connection lost
        p.waitForNotifications(0.001)

    # Apparently the destructor of p does not call disconnect()
    p.disconnect()
    # Should be stopped by now, but just in case
    key_manager.stop()
    # close csv file
    my_delegate.pkt_processor.close()

    print('Disconnected... Good Bye!')


if __name__ == '__main__':
    main()
