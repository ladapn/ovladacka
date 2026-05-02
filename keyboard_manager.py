import queue
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

KEY_TO_ROBOT_COMMAND = {
    QtCore.Qt.Key.Key_Up: b':a!',
    QtCore.Qt.Key.Key_Down: b':c!',
    QtCore.Qt.Key.Key_Right: b':b!',
    QtCore.Qt.Key.Key_Left: b':d!',
    QtCore.Qt.Key.Key_Space: b':e!',
    QtCore.Qt.Key.Key_Shift: b':f!'
}
TERMINATION_KEY = QtCore.Qt.Key.Key_Escape


def key_to_robot_command(key):
    return KEY_TO_ROBOT_COMMAND.get(key, None)


class TerminationRequested(Exception):
    pass


class KeyboardWidget(QtWidgets.QWidget):
    key_pressed = QtCore.pyqtSignal(int)
    window_closed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Ovladacka Keyboard Control')
        self.setFixedSize(340, 100)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        label = QtWidgets.QLabel(
            'Focus this window and press Arrow keys, Space, Shift or Escape to exit.',
            self
        )
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)

    def keyPressEvent(self, event):
        key = event.key()
        self.key_pressed.emit(key)
        event.accept()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()


class KeyboardManager:
    def __init__(self):
        self.key_queue = queue.Queue()

        self.app = QtWidgets.QApplication.instance()
        self._owns_app = False
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)
            self._owns_app = True

        self.widget = KeyboardWidget()
        self.widget.key_pressed.connect(self.on_press)
        self.widget.window_closed.connect(self.on_window_closed)

    def _format_key_text(self, key):
        key_text = QtGui.QKeySequence(key).toString()

        # Prevent UnicodeEncodeError when printing certain keys in some environments
        if key_text:
            try:
                key_text.encode('utf-8')
            except UnicodeEncodeError:
                key_text = key_text.encode('utf-8', errors='replace').decode('utf-8')

        return key_text

    def on_press(self, key):
        key_text = self._format_key_text(key)
        print(f'{key_text} pressed')
        self.key_queue.put(key)

    def on_window_closed(self):
        print('Window closed, exiting...')
        self.key_queue.put(TERMINATION_KEY)

    def start(self):
        self.widget.show()
        self.widget.activateWindow()
        self.widget.raise_()
        self.widget.setFocus()

    def stop(self):
        self.widget.close()
        if self._owns_app:
            self.app.quit()

    def get_key_nowait(self):
        self.app.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents)

        try:
            key = self.key_queue.get_nowait()
            if key == TERMINATION_KEY:
                raise TerminationRequested
        except queue.Empty:
            key = None
        return key

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
