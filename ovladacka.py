from bluepy import btle
from queue import Queue, Empty
from pynput.keyboard import Key, Listener
import time
import csv

import struct
import atexit

q = Queue()
known_packet_id = [101, 102]

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
        self.out_file = open(time.strftime("%Y-%m-%d-%H-%M-%S") + '.csv', 'w')
        self.csv_writer = csv.writer(self.out_file)
        # Destructor???

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print("data received")
        print(data)

        # get byte, check ID, if known id, get its length
        # knowing length, check CRC -> if ok, packet ok -> extract;
        # if not, go back to ID crawling
        remaining_data = data

        idx = 0
        while idx < len(data):
            if data[idx] in known_packet_id:
                # get packet len - TODO
                packet_len = 10;
                # check CRC!!! TODO
                packet = data[idx: idx + packet_len]

                # '<' means little endian AND no padding
                try:
                    print(list(struct.unpack('<BIIB', packet)))
                    self.csv_writer.writerow(list(struct.unpack('<BIIB', packet)))
                except struct.error as e:
                    # TODO: sometimes it sends 2 (or more?) packets in one go -> how often, do I need to deal with that?
                    print('something bad has happen while receiving data: {0}'.format(e))

                idx = idx + packet_len - 1

            idx = idx + 1


    # better design needed... -> one object that would go to with in main statement
    #@atexit.register
    def close(self):
        self.out_file.close()


def KeyTranslator(key):
    return {
        Key.up: b'A',
        Key.down: b'C',
        Key.right: b'B',
        Key.left: b'D',
        Key.space: b'E'
    }.get(key, None)  # TODO add other commands too


def on_press(key):
    print('{0} pressed'.format(
        key))
    # global q
    if key == Key.esc:
        q.put(None)
        return False
    else:
        q.put(key)


# =============================================================================
address = '00:13:AA:00:12:27'
service_uuid = btle.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')
char_uuid = btle.UUID('0000ffe1-0000-1000-8000-00805f9b34fb')

print('Attempting to connect to {0}'.format(address))
p = btle.Peripheral(address)

print('Connected Successfully')

my_delegate = MyDelegate()
p.setDelegate(MyDelegate())


svc = p.getServiceByUUID(service_uuid)
ch = svc.getCharacteristics(char_uuid)[0]

# Enable notifications for the characteristics
# Without this nothing happens when device sends data to PC...
p.writeCharacteristic(ch.valHandle + 1, b"\x01\x00")
#
# =============================================================================

listener = Listener(
    on_press=on_press)

listener.start()

while True:

    try:
        k = q.get_nowait()
        if k:
            cmd = KeyTranslator(k)
            if cmd:
                print(cmd)
                ch.write(cmd)
        else:
            break
    except Empty:
        pass

    # TODO: reconnect when connection lost
    p.waitForNotifications(0.001)

# Apparently the destructor of p does not call disconnect()
p.disconnect()
# Should be stopped by now, but just in case
listener.stop()
#close csv file
my_delegate.close()

print('Disconnected... Good Bye!')