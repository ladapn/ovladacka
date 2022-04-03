from abc import ABC, abstractmethod
import struct


class ParserException(Exception):
    pass


class ParserBadChecksum(Exception):
    pass


class PacketParser(ABC):
    def parse_raw_data(self, packet_id, raw_data):
        if not PacketParser.verify_checksum(raw_data):
            raise ParserBadChecksum

        return self.parse_core(packet_id, raw_data)

    @abstractmethod
    def parse_core(self, packet_id, raw_data):
        pass

    @staticmethod
    def unpack_bytes(packet_format, packet_id, raw_packet):
        try:
            packet_data = list(struct.unpack(packet_format, raw_packet))
        except struct.error as ex:
            raise ParserException(ex.__str__())

        return packet_data

    @staticmethod
    def verify_checksum(packet):
        checksum = packet[0]
        # Don't include last bit, that's the checksum
        for b in packet[1:-1]:
            checksum ^= b

        # Compare checksum with last byte -> checksum byte
        return checksum == packet[-1]


class UsndPacketParser(PacketParser):
    def parse_core(self, packet_id, raw_data):
        return PacketParser.unpack_bytes('<BIIB', packet_id, raw_data)


class StatusPacketParser(PacketParser):
    def parse_core(self, packet_id, raw_data):
        packet_data = PacketParser.unpack_bytes('<BIIHHHB', packet_id, raw_data)
        print(f'SW version: {packet_data[2]:07x}')
        return packet_data


