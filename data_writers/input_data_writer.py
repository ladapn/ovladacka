from data_writers import packet_writer
import time
import pathlib


def prepare_output_folder(master_folder='robot_outputs'):
    time_string = time.strftime("%Y-%m-%d-%H-%M-%S")
    path = pathlib.Path(master_folder + '/' + time_string)
    path.mkdir(parents=True, exist_ok=True)

    return master_folder + '/' + time_string + '/' + time_string


class InputDataWriter:
    def __init__(self, packet_info, path):
        self.id_to_writer = {}

        # fixme -> shouldn't be nescessary...
        usnd_packet_ids = [100, 101, 102, 103]
        usnd_writer = None

        for packet_id in packet_info:
            if packet_info[packet_id]['writer'] == 'generic':
                self.id_to_writer[packet_id] = packet_writer.StatusPacketWriter(path + '_' + packet_info[packet_id]['name'],
                                                                                packet_info[packet_id]['header'])
            elif packet_info[packet_id]['writer'] == 'ultrasound':
                if not usnd_writer:
                    usnd_writer = packet_writer.USNDPacketWriter(path + '_' + packet_info[packet_id]['name'],
                                                                 usnd_packet_ids)

                self.id_to_writer[packet_id] = usnd_writer

        # FIXME vytvor primo instanci podle jmena

    def write(self, packets):
        for packet_id, packet_data in packets:
            self.id_to_writer[packet_id].write_packet(packet_id, packet_data)

    def close(self):
        for packet_id in self.id_to_writer:
            self.id_to_writer[packet_id].close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
