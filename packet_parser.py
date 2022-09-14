import struct


class ParserException(Exception):
    pass


class ParserBadChecksum(Exception):
    pass


def parse_raw_data(packet_id, packet_structure, raw_data):
    if not verify_checksum(raw_data):
        raise ParserBadChecksum

    return unpack_bytes(packet_structure, packet_id, raw_data)


def unpack_bytes(packet_format, packet_id, raw_packet):
    try:
        packet_data = list(struct.unpack(packet_format, raw_packet))
    except struct.error as ex:
        raise ParserException(ex.__str__())

    return packet_data


def verify_checksum(packet):
    checksum = packet[0]
    # Don't include last bit, that's the checksum
    for b in packet[1:-1]:
        checksum ^= b

    # Compare checksum with last byte -> checksum byte
    return checksum == packet[-1]


