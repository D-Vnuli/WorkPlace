from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSystemTrayIcon,
    QStyle,
    QHeaderView
)


class OfflineDevicesDialog(QDialog):

    def __init__(self, title, devices, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(600, 350)

        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()

        icon_label = QLabel("⚠")
        icon_label.setStyleSheet("""
            font-size: 24px;
            color: #B00020;
        """)

        title_label = QLabel("Потеря связи")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #B00020;
        """)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        description = QLabel(
            f"Недоступно устройств: {len(devices)}"
        )

        description.setStyleSheet("""
            font-size: 14px;
            margin-bottom: 8px;
        """)

        layout.addWidget(description)

        self.table = QTableWidget()
        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels([
            "Устройство",
            "IP адрес"
        ])

        self.table.setRowCount(len(devices))

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)

        self.table.setStyleSheet("""
        QHeaderView::section {
            background-color: #F0F0F0;
            border: 1px solid #C8C8C8;
            padding: 4px;
            font-weight: bold;
        }

        QTableWidget {
            gridline-color: #D0D0D0;
        }
        """)

        table_header = self.table.horizontalHeader()

        table_header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        table_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )

        table_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        for row_index, device in enumerate(devices):
            _, name, ip = device

            name_item = QTableWidgetItem(name)
            ip_item = QTableWidgetItem(ip if ip else "")

            name_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            ip_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.table.setItem(
                row_index,
                0,
                name_item
            )

            self.table.setItem(
                row_index,
                1,
                ip_item
            )

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setFixedWidth(120)

        self.btn_ok.clicked.connect(
            self.accept
        )

        button_layout.addWidget(self.btn_ok)
        layout.addLayout(button_layout)


class NotificationManager:

    def device_online(self, device_id, name, ip):
        self.tray_icon.showMessage(
            "Связь восстановлена",
            f"{name}\nIP: {ip}\nУстройство снова в сети",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )

    def __init__(self, parent):
        self.parent = parent

        self.tray_icon = QSystemTrayIcon(parent)

        icon = QIcon(
            "icons/icon-monitor.png"
        )
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Network Monitor")
        self.tray_icon.show()

        self.pending_offline_devices = []

        self.offline_timer = QTimer(parent)
        self.offline_timer.setSingleShot(True)

        self.offline_timer.timeout.connect(
            self.show_grouped_offline_notification
        )

        self.active_popups = []

    def device_offline(
            self,
            device_id,
            name,
            ip):

        self.pending_offline_devices.append(
            (device_id, name, ip)
        )

        if not self.offline_timer.isActive():
            self.offline_timer.start(2000)

    def show_grouped_offline_notification(self):

        if not self.pending_offline_devices:
            return

        devices = self.pending_offline_devices.copy()
        self.pending_offline_devices.clear()

        device_ids = [
            device[0]
            for device in devices
        ]

        count = len(devices)

        if count == 1:
            title = "Устройство недоступно"
        else:
            title = f"Недоступно устройств: {count}"

        message = self.build_tray_message(devices)

        QApplication.beep()

        self.show_tray_message(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Warning,
            10000
        )

        self.show_popup(
            title,
            devices,
            device_ids
        )

    def build_tray_message(self, devices):

        if len(devices) == 1:
            _, name, ip = devices[0]

            return (
                f"{name}\n"
                f"{ip}\n"
                f"Потеряна связь"
            )

        lines = []

        for _, name, ip in devices:
            lines.append(
                f"• {name} — {ip}"
            )

        return "\n".join(lines)

    def show_popup(
            self,
            title,
            devices,
            device_ids):

        dialog = OfflineDevicesDialog(
            title,
            devices,
            self.parent
        )

        dialog.accepted.connect(
            lambda: self.parent.db.acknowledge_notifications(device_ids)
        )

        dialog.finished.connect(
            lambda: self.parent.db.acknowledge_notifications(device_ids)
        )

        self.active_popups.append(dialog)

        dialog.destroyed.connect(
            lambda: self.remove_popup(dialog)
        )

        dialog.show()

    def device_online(
            self,
            name,
            ip):

        title = "Связь восстановлена"

        message = (
            f"{name}\n"
            f"{ip}\n"
            f"Устройство снова в сети"
        )

        self.show_tray_message(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            6000
        )

    def show_tray_message(
            self,
            title,
            message,
            icon,
            timeout):

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title,
                message,
                icon,
                timeout
            )

    def remove_popup(
            self,
            dialog):

        if dialog in self.active_popups:
            self.active_popups.remove(dialog)