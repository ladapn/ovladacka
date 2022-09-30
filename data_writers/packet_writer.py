import csv
import pandas as pd
from abc import ABC, abstractmethod


class PacketWriter(ABC):
    """
    Interface defining packet writers
    """
    @abstractmethod
    def write_packet(self, packet_id, packet_data):
        """
        Store packet data somewhere (file, database...)
        :param packet_id: packet id
        :param packet_data: list of values of packet fields
        """
        pass

    @abstractmethod
    def close(self):
        """
        Perform operation needed before writer lifetime ends - usually close a file 
        """
        pass


class USNDPacketWriter(PacketWriter):
    """
    Writer for ultrasound measurement packets
    """
    def __init__(self, path, usnd_packet_ids):
        """
        Constructor method
        :param path: path including name of the output file without extension
        :param usnd_packet_ids: list of all packet ids that can contain ultrasound measurement data
        """
        self.data_frame_dict = {}
        self.usnd_packet_ids = usnd_packet_ids
        self.closed = False
        self.path = path

    def write_packet(self, packet_id, packet_data):
        """
        Add measurement to measurement database
        :param packet_id: packet id
        :param packet_data: list of values of packet fields
        """
        # TODO: work directly with DataFrame
        timestamp = packet_data[1]
        measurement = packet_data[2]
        if timestamp in self.data_frame_dict:
            self.data_frame_dict[timestamp][packet_id] = measurement
        else:
            self.data_frame_dict[timestamp] = dict.fromkeys(self.usnd_packet_ids, None)
            self.data_frame_dict[timestamp][packet_id] = measurement

    def close(self):
        """
        Dump measurement database to csv file
        """
        if not self.closed:
            data_frame = pd.DataFrame(self.data_frame_dict)
            data_frame = data_frame.transpose()
            data_frame.index.name = 'tick_ms'
            # Add a column containing minimum of the other columns
            data_frame.columns = ['front', 'right_front', 'right_center', 'right_back']
            data_frame['right_min'] = data_frame[['right_front', 'right_center', 'right_back']].min(axis=1)
            data_frame.to_csv(self.path + '.csv')
            self.closed = True


class StatusPacketWriter(PacketWriter):
    def __init__(self, path, header):
        """
        Constructor method
        :param str path: path including name of the output file without extension
        :param list[str] header: list of strings corresponding to names of columns in csv header
        """
        self.status_file = open(path + '.csv', 'w')
        self.status_csv = csv.writer(self.status_file)
        self.status_csv.writerow(header)

    def write_packet(self, packet_id, packet_data):
        """
        Write packet data to csv file
        :param int packet_id: packed id, currently not used
        :param packet_data: list of values of packet fields
        :return:
        """
        self.status_csv.writerow(packet_data)

    def close(self):
        """
        Close the output csv file
        """
        self.status_file.close()

