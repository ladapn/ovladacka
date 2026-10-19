import unittest
from connection import btle_connection

NUS_RX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
NUS_TX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
HM10_CHAR = '0000FFE1-0000-1000-8000-00805F9B34FB'


class CharacteristicUuidsTestCase(unittest.TestCase):
    def test_single_characteristic(self):
        self.assertEqual(btle_connection.characteristic_uuids({'char_uuid': HM10_CHAR}), (HM10_CHAR, HM10_CHAR))

    def test_separate_rx_tx_characteristics(self):
        config = {'rx_char_uuid': NUS_RX, 'tx_char_uuid': NUS_TX}
        self.assertEqual(btle_connection.characteristic_uuids(config), (NUS_RX, NUS_TX))

    def test_missing_characteristics(self):
        self.assertRaises(KeyError, btle_connection.characteristic_uuids, {'rx_char_uuid': NUS_RX})


if __name__ == '__main__':
    unittest.main()
