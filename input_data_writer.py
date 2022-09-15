import packet_writer
import time
import pathlib


def prepare_output_folder(master_folder='robot_outputs'):
    time_string = time.strftime("%Y-%m-%d-%H-%M-%S")
    path = pathlib.Path(master_folder + '/' + time_string)
    path.mkdir(parents=True, exist_ok=True)

    return master_folder + '/' + time_string + '/' + time_string


class InputDataWriter:
    def __init__(self, id_to_writer_type, path): # plus header...
        self.id_to_writer = {}

        # fixme -> shouldn't be nescessary...
        usnd_packet_ids = [100, 101, 102, 103]
        usnd_writer = packet_writer.USNDPacketWriter(path, usnd_packet_ids)

        for packet_id in id_to_writer_type:
            if id_to_writer_type[packet_id]['writer'] == 'generic':
                self.id_to_writer[packet_id] = packet_writer.StatusPacketWriter(path)
            elif id_to_writer_type[packet_id]['writer'] == 'ultrasound':
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
