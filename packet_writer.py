import csv
import pandas as pd
from abc import ABC, abstractmethod


class PacketWriter(ABC):
    @abstractmethod
    def write_packet(self, packet_id, packet_data):
        pass

    @abstractmethod
    def close(self):
        pass


class USNDPacketWriter(PacketWriter):
    def __init__(self, path, usnd_packet_ids):
        self.data_frame_dict = {}
        self.usnd_packet_ids = usnd_packet_ids
        self.closed = False
        self.path = path

    def write_packet(self, packet_id, packet_data):
        # TODO: work directly with DataFrame
        timestamp = packet_data[1]
        measurement = packet_data[2]
        if timestamp in self.data_frame_dict:
            self.data_frame_dict[timestamp][packet_id] = measurement
        else:
            self.data_frame_dict[timestamp] = dict.fromkeys(self.usnd_packet_ids, None)
            self.data_frame_dict[timestamp][packet_id] = measurement

    def close(self):
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
        self.status_file = open(path + '.csv', 'w')
        self.status_csv = csv.writer(self.status_file)
        self.status_csv.writerow(header)

    def write_packet(self, packet_id, packet_data):
        self.status_csv.writerow(packet_data)

    def close(self):
        self.status_file.close()

