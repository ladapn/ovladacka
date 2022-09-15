import unittest
from unittest.mock import patch, mock_open, call
import packet_writer


class PacketWriterTestCase(unittest.TestCase):
    def test_status_packet_writer(self):
        expected_calls = [call('id,tick_ms,commit_id,battery_v_adc,total_i_adc,motor_i_adc,crc\r\n'),
                          call('80,433439,178771540,117,0,0,142\r\n')]

        with patch('packet_writer.open', mock_open()) as mocked_file:
            status_writer = packet_writer.StatusPacketWriter('/mock/path')
            status_writer.write_packet(80, [80, 433439, 178771540, 117, 0, 0, 142])
            status_writer.close()

        mocked_file().write.assert_has_calls(expected_calls)

    def test_usnd_packet_writer(self):
        ultrasound_writer = packet_writer.USNDPacketWriter('/mock/path', [100, 101, 102, 103])
        ultrasound_writer.write_packet(100, [100, 35267, 117, 91])
        ultrasound_writer.write_packet(101, [101, 35267, 100, 91])

        expected_dict = {35267: {100: 117,
                                 101: 100,
                                 102: None,
                                 103: None}
                         }

        self.assertDictEqual(expected_dict, ultrasound_writer.data_frame_dict)





if __name__ == '__main__':
    unittest.main()
