from abc import ABC, abstractmethod


class RobotConnection(ABC):
    @abstractmethod
    def connect(self, number_of_retries=3):
        pass

    @abstractmethod
    def wait_for_notifications(self, timeout):
        pass

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

