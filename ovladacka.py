from bluepy import btle
from queue import Queue, Empty
from pynput.keyboard import Key, Listener

import struct

q = Queue()


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate._ _init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print("data received")
        print(data)
        # '<' means little endian AND no padding
        print(struct.unpack('<BIIB', data))


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

p.setDelegate(MyDelegate(0))

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

print('Disconnected... Good Bye!')
