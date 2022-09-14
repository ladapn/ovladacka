import unittest
import incoming_data_processor


class InputDataProcessorTestCase(unittest.TestCase):
    def test_process_incoming_data(self):
        input_data_processor = incoming_data_processor.InputDataProcessor()

        processed_data = input_data_processor.\
            process_incoming_data(data=b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00\x00\x00\x8ed\xc3\x89\x00\x00u\x00\x00\x00[')

        self.assertCountEqual(processed_data,
                              [(80, [80, 433439, 178771540, 117, 0, 0, 142]),
                               (100, [100, 35267, 117, 91])]
                              )


if __name__ == '__main__':
    unittest.main()
