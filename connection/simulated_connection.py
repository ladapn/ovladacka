from connection.robot_connection import RobotConnection


class SimConnection(RobotConnection):
    def __init__(self, data_queue):
        self.data_queue = data_queue

    def connect(self, number_of_retries=3):
        pass

    def wait_for_notifications(self, timeout):
        data = b'P\x1f\x9d\x06\x00T\xd6\xa7\nu\x00\x00\x00\x00\x00\x8e'
        self.data_queue.put(data)

    def write(self, data):
        pass

    def disconnect(self):
        pass

