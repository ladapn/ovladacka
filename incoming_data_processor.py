import packet_writer
import packet_parser


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
