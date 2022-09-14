import io
import unittest
import unittest.mock
import incoming_data_processor


class InputDataProcessorTestCase(unittest.TestCase):
    def test_process_incoming_data(self):
        packet_definition = {100: {"structure": "<BIIB",
                                   "length": 10},
                             80: {"structure": "<BIIHHHB",
                                  "length": 16}
                             }
        input_data_processor = incoming_data_processor.InputDataProcessor(packet_definition)

        processed_data = input_data_processor.process_incoming_data(data=b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00'
                                                                         b'\x00\x00\x8ed\xc3\x89\x00\x00u\x00\x00\x00[')

        self.assertCountEqual(processed_data,
                              [(80, [80, 433439, 178771540, 117, 0, 0, 142]),
                               (100, [100, 35267, 117, 91])]
                              )

    def test_process_incoming_data_two_bursts(self):
        packet_definition = {100: {"structure": "<BIIB",
                                   "length": 10},
                             80: {"structure": "<BIIHHHB",
                                  "length": 16}
                             }
        input_data_processor = incoming_data_processor.InputDataProcessor(packet_definition)

        processed_data = input_data_processor.\
            process_incoming_data(data=b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00\x00\x00\x8ed\xc3\x89')

        processed_data += input_data_processor.\
            process_incoming_data(data=b'\x00\x00u\x00\x00\x00[')

        self.assertCountEqual(processed_data,
                              [(80, [80, 433439, 178771540, 117, 0, 0, 142]),
                               (100, [100, 35267, 117, 91])]
                              )

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_process_incoming_bad_checksum(self, mock_stdout):
        packet_definition = {100: {"structure": "<BIIB",
                                   "length": 10},
                             80: {"structure": "<BIIHHHB",
                                  "length": 16}
                             }
        input_data_processor = incoming_data_processor.InputDataProcessor(packet_definition)
        processed_data = input_data_processor. \
            process_incoming_data(data=b'd\xc3\x89\x00\x00u\x00\x00\x006')
        self.assertTrue('Broken checksum found, Packet ID: 100' in mock_stdout.getvalue())



if __name__ == '__main__':
    unittest.main()
