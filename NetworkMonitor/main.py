import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.styles import APP_STYLE
from ui.main_window import MainWindow


APP_ID = "NetworkMonitorSingleInstance"


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    socket = QLocalSocket()
    socket.connectToServer(APP_ID)

    if socket.waitForConnected(500):
        QMessageBox.warning(
            None,
            "Network Monitor",
            "Приложение уже запущено."
        )
        socket.disconnectFromServer()
        sys.exit(0)

    QLocalServer.removeServer(APP_ID)

    server = QLocalServer()
    server.listen(APP_ID)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()