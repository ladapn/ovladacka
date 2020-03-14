from bluepy import btle
import pygame    


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print("data received")
        print(data)

def KeyTranslator(key):
    return {
        273: b'A',
        274: b'C',
        275: b'B',
        276: b'D'
    }.get(key, None) #TODO add other commands too

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

# Prepare pygame
pygame.init()
screen = pygame.display.set_mode((100, 100))

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            print(event.key)
# TODO implement switch as a dictionary
            if event.key == 27:  # Esc
                done = True
                break
            cmd = KeyTranslator(event.key)
            if cmd != None:
                ch.write(cmd)
        elif event.type == pygame.QUIT:
            done = True

#
#while True:
#    if p.waitForNotifications(1.0):
        # handleNotification() was called
#        continue

#    print("Waiting...")
    # Perhaps do something else here
