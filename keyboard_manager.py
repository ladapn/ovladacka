from pynput.keyboard import Key, Listener
import queue


def key_translator(key):
    return {
        Key.up: b'A',
        Key.down: b'C',
        Key.right: b'B',
        Key.left: b'D',
        Key.space: b'E'
    }.get(key, None)


class KeyboardManagerEnded(Exception):
    pass


class KeyboardManager:
    def __init__(self):
        self.key_queue = queue.Queue()
        self.listener = Listener(on_press=self.on_press)

    def on_press(self, key):
        """Callback to handle key press event"""
        print(f'{key} pressed')

        self.key_queue.put(key)

        if key == Key.esc:
            return False
        else:
            return True

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def get_key_nowait(self):
        try:
            key = self.key_queue.get_nowait()
            if key == Key.esc:
                raise KeyboardManagerEnded
        except queue.Empty:
            key = None
        return key

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
