from data_writers import packet_writer
import pathlib


def prepare_output_folder(data_folder_name, master_folder_name='robot_outputs'):
    """
    Create output folder structure. If the folders do not exist yet, create them
    :param data_folder_name: name of a folder to hold files with robot data for each run of ovladacka
    :param master_folder_name: name of folder to hold all data folders from all runs of ovladacka, defaults to
    "robot_outputs"
    :return: string form of path to data folder - i.e. "master_folder_name/data_folder_name/"
    """
    path = pathlib.Path(master_folder_name + '/' + data_folder_name)
    path.mkdir(parents=True, exist_ok=True)

    return master_folder_name + '/' + data_folder_name + '/'


class InputDataWriter:
    """
    Class to write input (i.e. data coming from robot) data into files
    """
    def __init__(self, packet_info, path, filename_prefix):
        """
        Constructor method
        :param packet_info: dictionary of dictionaries, where first key is packet id, second is packet information type.
        At least "writer", "name" and "header" second keys must be present. See doc/packet_definition.md for more
        information on these fields
        :param str path: path folder to hold all output files
        :param str filename_prefix: common prefix for names of all output files
        """
        self.id_to_writer = {}

        # fixme -> shouldn't be nescessary...
        usnd_packet_ids = [100, 101, 102, 103]
        usnd_writer = None

        for packet_id in packet_info:
            if packet_info[packet_id]['writer'] == 'generic':
                self.id_to_writer[packet_id] = packet_writer.StatusPacketWriter(path + filename_prefix + '_' +
                                                                                packet_info[packet_id]['name'],
                                                                                packet_info[packet_id]['header'])
            elif packet_info[packet_id]['writer'] == 'ultrasound':
                if not usnd_writer:
                    usnd_writer = packet_writer.USNDPacketWriter(path + filename_prefix + '_' +
                                                                 packet_info[packet_id]['name'],
                                                                 usnd_packet_ids)

                self.id_to_writer[packet_id] = usnd_writer

    def write(self, packets):
        """
        Write parsed packet data using dedicated writer (determined by packet id)
        :param packets: list of tuples, where first tuple element is packet id and the other one is a list of packet
        field values
        """
        for packet_id, packet_data in packets:
            self.id_to_writer[packet_id].write_packet(packet_id, packet_data)

    def close(self):
        """
        Close all writers
        """
        for packet_id in self.id_to_writer:
            self.id_to_writer[packet_id].close()

    def __enter__(self):
        """
        When entering context manager no additional operation is performed
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When exiting context manager close all writers
        """
        self.close()
