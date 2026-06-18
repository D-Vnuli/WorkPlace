import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.styles import LIGHT_STYLE, DARK_STYLE
from database import Database
from ui.main_window import MainWindow


APP_ID = "NetworkMonitorSingleInstance"


def main():
    app = QApplication(sys.argv)

    db = Database()
    theme = db.get_setting("theme", "light")

    if theme == "dark":
        app.setStyleSheet(DARK_STYLE)
    else:
        app.setStyleSheet(LIGHT_STYLE)

    socket = QLocalSocket()
    socket.connectToServer(APP_ID)

    if socket.waitForConnected(500):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Network Monitor")
        msg.setText("Приложение уже запущено.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
        QMessageBox {
            background-color: #FFFFFF;
        }

        QLabel {
            color: #111827;
            font-size: 10pt;
        }

        QPushButton {
            background-color: #2563EB;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 7px 16px;
            min-width: 80px;
        }
        """)

        msg.exec()
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