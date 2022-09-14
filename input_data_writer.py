import packet_writer


class InputDataWriter:
    def __init__(self, id_to_writer_type): # plus header...
        self.id_to_writer = {}

        # fixme
        usnd_packet_ids = [100, 101, 102, 103]

        for packet_id in id_to_writer_type:
            if id_to_writer_type[packet_id]['writer'] == 'generic':
                self.id_to_writer[packet_id] = packet_writer.StatusPacketWriter() # FIXME separate instances?
            elif id_to_writer_type[packet_id]['writer'] == 'ultrasound':
                self.id_to_writer[packet_id] = packet_writer.USNDPacketWriter(usnd_packet_ids)

    def write(self, packets):
        for packet_id, packet_data in packets:
            self.id_to_writer[packet_id].write(packet_data)

    def close(self):
        for packet_id in self.id_to_writer:
            self.id_to_writer[packet_id].close()
