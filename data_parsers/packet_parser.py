import struct


class ParserException(Exception):
    """
    Exception to be thrown when a packet cannot be parsed for any reason (e.g. incoming data is shorter
    than incoming data). Method __str__() holds the actual reason
    """
    pass


class ParserBadChecksum(Exception):
    """
    Exception to be thrown when a packet has a broken checksum
    """
    pass


def parse_raw_data(packet_structure, raw_data):
    """
    Parse - i.e. convert sequence of bytes to list of fields holding packet values
    :param str packet_structure: format string used by struct package
    (see https://docs.python.org/3/library/struct.html) to decode packet field from raw data
    :param bytes raw_data: raw packet data as a sequence of bytes
    :raise ParserBadChecksum: exception thrown when the packet has a broken checksum
    :raise ParserException: exception thrown when packet cannot be parsed for any reason (e.g. incoming data is shorter
    than incoming data). Method __str__() holds the actual reason
    :return: list of parsed packet fields
    """
    if not verify_checksum(raw_data):
        raise ParserBadChecksum

    try:
        packet_data = list(struct.unpack(packet_structure, raw_data))
    except struct.error as ex:
        raise ParserException(ex.__str__())

    return packet_data


def verify_checksum(packet):
    """
    Verify packet checksum - XOR all bytes (except the last one) and compare the result to the last byte that holds the
    check sum computed by robot
    :param bytes packet: raw packet data
    :return bool: True if checksum computed by this function matches checksum field of the packet
    """
    checksum = packet[0]
    # Don't include last byte, that's the checksum
    for b in packet[1:-1]:
        checksum ^= b

    # Compare checksum with last byte -> checksum byte
    return checksum == packet[-1]


