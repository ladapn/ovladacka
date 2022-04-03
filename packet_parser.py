from abc import ABC, abstractmethod
import struct


class ParserException(Exception):
    pass


class PacketParser(ABC):
    @abstractmethod
    def parse_raw_data(self, packet_id, raw_data):
        pass

    @staticmethod
    def unpack_bytes(packet_format, packet_id, raw_packet):
        try:
            packet_data = list(struct.unpack(packet_format, raw_packet))
        except struct.error as ex:
            print(f'something bad has happened while processing data of packet ID {packet_id}: {ex}')
            raise ParserException(ex.__str__())

        return packet_data


class UsndPacketParser(PacketParser):
    def parse_raw_data(self, packet_id, raw_data):
        return PacketParser.unpack_bytes('<BIIB', packet_id, raw_data)


class StatusPacketParser(PacketParser):
    def parse_raw_data(self, packet_id, raw_data):
        packet_data = PacketParser.unpack_bytes('<BIIHHHB', packet_id, raw_data)
        print(f'SW version: {packet_data[2]:07x}')
        return packet_data


