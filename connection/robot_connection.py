from abc import ABC, abstractmethod


class RobotConnection(ABC):
    """
    Abstract class defining interface for connection to robot.
    """
    @abstractmethod
    def connect(self, number_of_retries=3):
        """
        Initiate connection to robot
        :param int number_of_retries: Total number of attempts to connect, if connection cannot be established,
        defaults to 3
        """
        pass

    @abstractmethod
    def wait_for_notifications(self, timeout):
        """
        Wait for notification that there are new data from robot available. The method blocks until
        new data is available, or until maximal waiting time elapses
        :param float timeout: maximal waiting time in seconds
        :return True if data received, False in case of timeout
        """
        pass

    @abstractmethod
    def write(self, data):
        """
        Send data to robot
        :param bytes data: data to be sent
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnects from robot
        """
        pass

    def __enter__(self):
        """
        If context manager is entered, initiate robot connection
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        If context manager is exited, disconnect from robot
        """
        self.disconnect()

