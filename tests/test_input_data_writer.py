import unittest
import input_data_writer
import pathlib


class InputDataWriterTestCase(unittest.TestCase):
    def test_write_status(self):
        packet_definition = {80: {"structure": "<BIIHHHB",
                                  "length": 16,
                                  "writer": "generic"}
                             }
        in_writer = input_data_writer.InputDataWriter(packet_definition, 'tests/test_status_file')
        in_writer.write([(80, [80, 433439, 178771540, 117, 0, 0, 142])])
        in_writer.close()

        test_file_name = 'tests/test_status_file' + '_stat.csv'
        with open(test_file_name, 'r') as test_file:
            actual = test_file.readlines()

        pathlib.Path(test_file_name).unlink()

        expected = ['id,tick_ms,commit_id,battery_v_adc,total_i_adc,motor_i_adc,crc\n',
                    '80,433439,178771540,117,0,0,142\n']

        self.assertEqual(actual, expected)

    def test_write_ultrasound(self):
        packet_definition = {100: {"structure": "<BIIB",
                                   "length": 10,
                                   "writer": "ultrasound"},
                             101: {"structure": "<BIIB",
                                   "length": 10,
                                   "writer": "ultrasound"},
                             102: {"structure": "<BIIB",
                                   "length": 10,
                                   "writer": "ultrasound"},
                             103: {"structure": "<BIIB",
                                   "length": 10,
                                   "writer": "ultrasound"},
                             }

        in_writer = input_data_writer.InputDataWriter(packet_definition, 'tests/test_file_usnd')
        in_writer.write([(100, [100, 35267, 117, 91]),
                         (101, [101, 35267, 118, 91]),
                         (102, [102, 35267, 119, 91]),
                         (103, [103, 35267, 120, 91])]
                        )
        in_writer.close()

        test_file_name = 'tests/test_file_usnd' + '_usnd.csv'
        with open(test_file_name, 'r') as test_file:
            actual = test_file.readlines()

        pathlib.Path(test_file_name).unlink()

        expected = ['tick_ms,front,right_front,right_center,right_back,right_min\n', '35267,117,118,119,120,118\n']

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
