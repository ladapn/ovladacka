from bluepy import btle
import keyboard_manager
import packet_writer
import packet_parser
# import queue

# FIXME - duplicty -> minimalne neco z tohoto muzu za cenu malych uprav vyhodit
usnd_packet_ids = [100, 101, 102, 103]
status_packet_ids = [80]

packet_lengths = {100: 10,
                  101: 10,
                  102: 10,
                  103: 10,
                  80: 16}

known_packet_id = usnd_packet_ids + status_packet_ids


class RobotCommDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.pkt_processor = PacketProcessor()

    def handleNotification(self, cHandle, data):
        self.pkt_processor.process_incoming_data(data)
        # TODO: put data to a queue
        # self.incoming_data_queue.add(data) -> a to bude vse, co tu bude


class PacketProcessor:
    def __init__(self):
        self.leftovers = None

        # TODO -> processor could be a class -> but then this class should be renamed to somehitng (InputDataProcessor?)
        # TODO -> put all these related classes to one module: packet_data_manager or input_data_processor
        usnd_processor = (packet_parser.UsndPacketParser(), packet_writer.USNDPacketWriter())

        # TODO iterovat pres usnd_packet_IDs
        self.packet_processors = {100: usnd_processor,
                                  101: usnd_processor,
                                  102: usnd_processor,
                                  103: usnd_processor,
                                  80: (packet_parser.StatusPacketParser(), packet_writer.StatusPacketWriter())
                                  }

    @staticmethod
    def verify_checksum(packet):
        checksum = packet[0]
        # Don't include last bit, that's the checksum
        for b in packet[1:-1]:
            checksum ^= b

        # Compare checksum with last byte -> checksum byte
        return checksum == packet[-1]

    def close(self):
        for parser, writer in self.packet_processors.values():
            writer.close()

    def process_packet(self, packet_id, packet):
        parser, writer = self.packet_processors[packet_id]
        packet_data = parser.parse_raw_data(packet_id, packet)
        print(packet_data)
        writer.write_packet(packet_id, packet_data)

    def process_incoming_data(self, data):

        # ... process 'data'
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
            if packet_id in known_packet_id:
                packet_len = packet_lengths[packet_id]
                packet = data[idx: idx + packet_len]

                # Is the packet contained in this data, or does it continue in the next burst?
                if idx + packet_len > len(data):
                    self.leftovers = data[idx:]
                    break

                if PacketProcessor.verify_checksum(packet):
                    self.process_packet(packet_id, packet)
                else:
                    print(f'Broken checksum found, Packet ID: {packet_id}')

                idx = idx + packet_len - 1

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
