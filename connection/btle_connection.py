from bluepy import btle
from connection.robot_connection import RobotConnection


class RobotCommDelegate(btle.DefaultDelegate):
    """
    Class implementing bluepy's DeafultDelegate interface. Its purpose is to encapsulate callback to handle data
    incoming from a remote device connected via Bluetooth Low Energy (BTLE).
    """
    def __init__(self, incoming_data_queue):
        """
        Constructor method
        :param queue.Queue incoming_data_queue: queue to hold data received from the device we are connecting to
        """
        btle.DefaultDelegate.__init__(self)
        self.incoming_data_queue = incoming_data_queue

    def handleNotification(self, cHandle, data):
        """
        Callback to process data received from a connected remote device
        :param int cHandle: characteristics handle to distinguish which characteristics of the connected device sent the
        data
        :param bytes data: data received from the device
        """
        self.incoming_data_queue.put(data)


class BTLEConnection(RobotConnection):
    """
    This is a class providing functionality to connect to and to communicate with a remote device via Bluetooth Low
    Energy (BTLE).
    """
    def __init__(self, address, service_uuid, characteristics_uuid, incoming_data_queue):
        """
        Constructor method
        :param str address: Hardware address of BTLE device in the following format: "00:00:00:00:00:00"
        :param str service_uuid: BTLE UUID of service we want to connect to, formatted as:
        "00000000-0000-0000-0000-000000000000"
        :param str characteristics_uuid: BTLE UUID of service we want to connect to, formatted as:
        "00000000-0000-0000-0000-000000000000"
        :param queue.Queue incoming_data_queue: queue to hold data received from the device we are connecting to
        """
        self.address = address
        self.service_uuid = btle.UUID(service_uuid)
        self.char_uuid = btle.UUID(characteristics_uuid)
        self.characteristics = None
        self.delegate = RobotCommDelegate(incoming_data_queue)
        self.peripheral = None

    def connect(self, number_of_retries=3):
        """
        Connect to peripheral and enable its notifications
        :param int number_of_retries: Total number of attempts to connect, if connection cannot be established,
        defaults to 3
        """
        for tries in range(number_of_retries):
            try:
                self.peripheral = btle.Peripheral(self.address)
                break
            except btle.BTLEDisconnectError as e:
                print(e)
                if tries == (number_of_retries - 1):
                    print('Giving up')
                    exit()  # FIXME throw exception instead -> and update docstring :raises
                print('Trying again...')

        self.peripheral.setDelegate(self.delegate)
        svc = self.peripheral.getServiceByUUID(self.service_uuid)
        self.characteristics = svc.getCharacteristics(self.char_uuid)[0]

        # Enable notifications for the characteristics
        # Without this nothing happens when device sends data to PC...
        self.peripheral.writeCharacteristic(self.characteristics.valHandle + 1, b"\x01\x00")

    def wait_for_notifications(self, timeout):
        """
        Wait for notification that there are new data from the connected device available. The method blocks until
        new data is available, or until maximal waiting time elapses
        :param float timeout: maximal waiting time in seconds
        :return True if data received, False in case of timeout
        """
        return self.peripheral.waitForNotifications(timeout)

    def write(self, data):
        """
        Send data to peripheral
        :param bytes data: data to be sent
        """
        self.characteristics.write(data)

    def disconnect(self):
        """Disconnects from peripheral"""
        self.peripheral.disconnect()
