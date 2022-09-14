import unittest
import packet_parser


class PacketParserTestCase(unittest.TestCase):
    def test_usnd_packet_parser(self):
        packet_data = packet_parser.parse_raw_data(packet_id=100, packet_structure='<BIIB',
                                            raw_data=b'd\xc3\x89\x00\x00u\x00\x00\x00[')
        self.assertCountEqual(packet_data, [100, 35267, 117, 91])

    def test_usnd_packet_parser_incomplete(self):
        self.assertRaises(packet_parser.ParserBadChecksum, packet_parser.parse_raw_data, packet_id=100,
                          packet_structure='<BIIB',
                          raw_data=b'd\xc3\x89\x00')

    def test_status_packet_parser(self):
        packet_data = packet_parser.parse_raw_data(packet_id=80,
                                            packet_structure='<BIIHHHB',
                                            raw_data=b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00\x00\x00\x8e')
        self.assertCountEqual(packet_data, [80, 433439, 178771540, 117, 0, 0, 142])


if __name__ == '__main__':
    unittest.main()
