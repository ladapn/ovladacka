import asyncio
import queue
import threading
import time
from bleak import BleakClient
from connection.robot_connection import RobotConnection


class BTLEConnection(RobotConnection):
    """
    This is a class providing functionality to connect to and to communicate with a remote device via Bluetooth Low
    Energy (BTLE) using the bleak library.
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
        self.service_uuid = service_uuid
        self.char_uuid = characteristics_uuid
        self.incoming_data_queue = incoming_data_queue
        self._data_event = threading.Event()
        self.client = None
        self.loop = None
        self.thread = None
        self._connected = False

    def _notification_handler(self, sender, data):
        """Callback for BLE notifications"""
        self.incoming_data_queue.put(data)
        self._data_event.set()

    def _run_async_loop(self):
        """Run the asyncio event loop in a background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _start_loop(self):
        """Start the background asyncio loop if it is not already running."""
        if self.loop and self.loop.is_running():
            return True

        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

        timeout = time.time() + 5
        while self.loop is None and time.time() < timeout:
            time.sleep(0.01)

        return self.loop is not None

    def _stop_loop(self):
        """Stop and clean up the background asyncio loop."""
        if self.loop:
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except RuntimeError:
                pass

        if self.thread:
            self.thread.join(timeout=5)

        if self.loop and not self.loop.is_closed():
            try:
                self.loop.close()
            except RuntimeError:
                pass

        self.loop = None
        self.thread = None

    def connect(self, number_of_retries=3):
        """
        Connect to peripheral and enable its notifications
        :param int number_of_retries: Total number of attempts to connect, if connection cannot be established,
        defaults to 3
        :return True if connection established, False if connection cannot be established
        """
        if self._connected:
            return True

        if not self._start_loop():
            print('Failed to start asyncio loop')
            return False

        for tries in range(number_of_retries):
            print(f'Trying to connect to peripheral {self.address}...')
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self._connect_async(),
                    self.loop
                )
                result = future.result()
                if result:
                    self._connected = True
                    return True
            except Exception as e:
                print(e)
                if tries == (number_of_retries - 1):
                    print('Giving up')
                    break
                print('Trying again...')

        self._stop_loop()
        return False

    async def _connect_async(self):
        """Async connection routine"""
        try:
            self.client = BleakClient(self.address)
            await self.client.connect()
            await self.client.start_notify(self.char_uuid, self._notification_handler)
            return True
        except Exception as e:
            self.client = None
            print(f'Connection error: {e}')
            return False

    def wait_for_notifications(self, timeout):
        """
        Wait for notification that there are new data from the connected device available.
        :param float timeout: maximal waiting time in seconds
        :return True if data received, False in case of timeout
        """
        result = self._data_event.wait(timeout=timeout)
        # Check if queue actually has data (event might be stale)
        if result or not self.incoming_data_queue.empty():
            self._data_event.clear()
            return True
        return False

    def write(self, data):
        """
        Send data to peripheral
        :param bytes data: data to be sent
        """
        if not self._connected or not self.client:
            raise RuntimeError('Not connected to device')

        future = asyncio.run_coroutine_threadsafe(
            self.client.write_gatt_char(self.char_uuid, data),
            self.loop
        )
        future.result()

    def disconnect(self):
        """Disconnects from peripheral"""
        if self._connected and self.client and self.loop:
            future = asyncio.run_coroutine_threadsafe(
                self.client.disconnect(),
                self.loop
            )
            try:
                future.result(timeout=5)
            except Exception as e:
                print(f'Disconnect error: {e}')

        self._connected = False
        self.client = None
        self._data_event.clear()
        self._stop_loop()
