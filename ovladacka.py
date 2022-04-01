from bluepy import btle
import keyboard_manager
import time
import csv
import pandas as pd
import struct
# import queue


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


class PacketWriter:
    def __init__(self):
        time_string = time.strftime("%Y-%m-%d-%H-%M-%S")
        self.usnd_file = open(time_string + '.csv', 'w')
        self.usnd_writer = csv.writer(self.usnd_file)
        self.usnd_writer.writerow(['id', 'tick_ms', 'distance_cm', 'crc'])
        self.data_frame_dict = {}

        self.status_file = open(time_string + '_stat.csv', 'w')
        self.status_csv = csv.writer(self.status_file)

        self.status_csv.writerow(['id', 'tick_ms', 'commit_id', 'battery_v_adc', 'total_i_adc', 'motor_i_adc', 'crc'])

    def write_usnd_packet(self, packet_id, packet_data):
        # TODO: work directly with DataFrame
        timestamp = packet_data[1]
        measurement = packet_data[2]
        if timestamp in self.data_frame_dict:
            self.data_frame_dict[timestamp][packet_id] = measurement
        else:
            self.data_frame_dict[timestamp] = dict.fromkeys(usnd_packet_ids, None)
            self.data_frame_dict[timestamp][packet_id] = measurement

        self.usnd_writer.writerow(packet_data)

    def write_status_packet(self, packet_data):
        self.status_csv.writerow(packet_data)

    def close(self):
        self.usnd_file.close()
        self.status_file.close()
        data_frame = pd.DataFrame(self.data_frame_dict)
        data_frame = data_frame.transpose()
        # Add a column containing minimum of the other columns
        # data_frame['Min'] = data_frame[['101', '102', '103']].min(axis=1)
        data_frame.columns = ['front', 'right_front', 'right_center', 'right_back']
        data_frame['Min'] = data_frame.min(axis=1)
        data_frame.to_csv(time.strftime("%Y-%m-%d-%H-%M-%S") + '_pd.csv')


class PacketProcessor:
    def __init__(self):
        self.leftovers = None
        self.packet_writer = PacketWriter()

    @staticmethod
    def unpack_bytes(packet_format, packet_id, raw_packet):
        try:
            packet_data = list(struct.unpack(packet_format, raw_packet))
        except struct.error as ex:
            print(f'something bad has happened while processing data of packet ID {packet_id}: {ex}')
            packet_data = None  # TODO get rid of return value -> just use exceptions

        return packet_data

    @staticmethod
    def verify_checksum(packet):
        checksum = packet[0]
        # Don't include last bit, that's the checksum
        for b in packet[1:-1]:
            checksum ^= b

        # Compare checksum with last byte -> checksum byte
        return checksum == packet[-1]

    def process_usnd_packet(self, packet, packet_id):
        packet_data = PacketProcessor.unpack_bytes('<BIIB', packet_id, packet)

        if packet_data:
            print(packet_data)
            self.packet_writer.write_usnd_packet(packet_id, packet_data)

    def process_status_packet(self, packet, packet_id):
        packet_data = PacketProcessor.unpack_bytes('<BIIHHHB', packet_id, packet)
        if packet_data:
            print(packet_data)
            # print('SW version: {:07x}'.format(packet_data[2]))
            print(f'SW version: {packet_data[2]:07x}')

            self.packet_writer.write_status_packet(packet_data)

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
                    if packet_id in usnd_packet_ids:
                        self.process_usnd_packet(packet, packet_id)
                    elif packet_id in status_packet_ids:
                        self.process_status_packet(packet, packet_id)
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
    my_delegate.pkt_processor.packet_writer.close()

    print('Disconnected... Good Bye!')


if __name__ == '__main__':
    main()
