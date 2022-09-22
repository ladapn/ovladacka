from connection.robot_connection import RobotConnection


class SimConnection(RobotConnection):
    """
    Implements a simulated connection to robot. This is intended to run ovladacka without robot mainly for testing and
    development purposes
    """
    def __init__(self, data_queue):
        """
        Constructor method
        :param queue.Queue data_queue: queue to hold data received from simulated robot
        """
        self.data_queue = data_queue

    def connect(self, number_of_retries=3):
        """
        In simulation mode, we do not connect to any device so this implementation of RobotConnection's connect does
        nothing
        """
        pass

    def wait_for_notifications(self, timeout):
        """
        Puts fake data in the data queue to simulate that robot sent something. Currently, one packet 80 with fixed data
        is used - i.e. everytime this method is called, the same data is put to the queue
        :param timeout:
        :return:
        """
        data = b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00\x00\x00\x8e'
        self.data_queue.put(data)

    def write(self, data):
        """
        Currently, the simulation does not implement sending data to robot so this implementation of RobotConnection's
        write does nothing
        """
        pass

    def disconnect(self):
        """
        In simulation mode, we do not connect to any device so this implementation of RobotConnection's disconnect does
        nothing
        """
        pass

