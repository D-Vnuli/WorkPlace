import subprocess
import time
import sys

from PyQt6.QtCore import QThread, pyqtSignal


class PingWorker(QThread):

    device_status_changed = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.running = True
        self.devices = []

    def stop(self):
        self.running = False

    def update_devices(self, devices):
        self.devices = devices.copy()

    def ping_host(self, ip):

        if not ip:
            return False

        try:
            creationflags = 0

            if sys.platform.startswith("win"):
                creationflags = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(
                [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    "1000",
                    ip
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags
            )

            return result.returncode == 0

        except Exception:
            return False

    def run(self):

        while self.running:

            devices = self.devices.copy()

            for device_id, ip in devices:

                if not self.running:
                    return

                online = self.ping_host(ip)

                if online:
                    self.device_status_changed.emit(
                        device_id,
                        "online"
                    )
                else:
                    self.device_status_changed.emit(
                        device_id,
                        "offline"
                    )

            for _ in range(20):

                if not self.running:
                    return

                time.sleep(1)