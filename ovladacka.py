from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print("data received")
        print(data)

address = '00:13:AA:00:12:27'
service_uuid = btle.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')
char_uuid = btle.UUID('0000ffe1-0000-1000-8000-00805f9b34fb')

p = btle.Peripheral( address )
p.setDelegate( MyDelegate(0) )

svc = p.getServiceByUUID( service_uuid )
ch = svc.getCharacteristics( char_uuid )[0]

# Enable notifications for the characteristics
# Without this nothing happens when device sends data to PC...
p.writeCharacteristic(ch.valHandle + 1, b"\x01\x00")


ch.write(b'B')
while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    print("Waiting...")
    # Perhaps do something else here
