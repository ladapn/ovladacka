from bluepy import btle
from connection.robot_connection import RobotConnection


class RobotCommDelegate(btle.DefaultDelegate):
    def __init__(self, incoming_data_queue):
        btle.DefaultDelegate.__init__(self)
        self.incoming_data_queue = incoming_data_queue

    def handleNotification(self, cHandle, data):
        self.incoming_data_queue.put(data)


class BTLEConnection(RobotConnection):
    def __init__(self, address, service_uuid, characteristics_uuid, queue):
        self.address = address
        self.service_uuid = btle.UUID(service_uuid)
        self.char_uuid = btle.UUID(characteristics_uuid)
        self.characteristics = None
        self.delegate = RobotCommDelegate(queue)
        self.peripheral = None

    def connect(self, number_of_retries=3):

        for tries in range(number_of_retries):
            try:
                self.peripheral = btle.Peripheral(self.address)
                break
            except btle.BTLEDisconnectError as e:
                print(e)
                if tries == (number_of_retries - 1):
                    print('Giving up')
                    exit()
                print('Trying again...')

        self.peripheral.setDelegate(self.delegate)
        svc = self.peripheral.getServiceByUUID(self.service_uuid)
        self.characteristics = svc.getCharacteristics(self.char_uuid)[0]

        # Enable notifications for the characteristics
        # Without this nothing happens when device sends data to PC...
        self.peripheral.writeCharacteristic(self.characteristics.valHandle + 1, b"\x01\x00")

    def wait_for_notifications(self, timeout):
        self.peripheral.waitForNotifications(timeout)

    def write(self, data):
        self.characteristics.write(data)

    def disconnect(self):
        self.peripheral.disconnect()


