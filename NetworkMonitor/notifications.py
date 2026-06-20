import os
import sys
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
    QHeaderView
)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class OfflineDevicesDialog(QDialog):

    def __init__(
            self,
            title,
            devices,
            dark_theme=False,
            parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.resize(900, 500)
        self.setMinimumSize(900, 500)

        if dark_theme:

            self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #F3F4F6;
            }

            QLabel {
                color: #F3F4F6;
            }

            QTableWidget {
                background-color: #252526;
                color: #F3F4F6;
                gridline-color: #3F3F46;
                border: 1px solid #3F3F46;
            }

            QTableWidget::item {
                color: #F3F4F6;
            }

            QHeaderView::section {
                background-color: #2D2D30;
                color: #F3F4F6;
                border: 1px solid #3F3F46;
                padding: 6px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
            }
            """)

        else:

            self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #111827;
            }

            QLabel {
                color: #111827;
            }

            QTableWidget {
                background-color: #FFFFFF;
                color: #111827;
                gridline-color: #D1D5DB;
                border: 1px solid #D1D5DB;
            }

            QTableWidget::item {
                color: #111827;
            }

            QHeaderView::section {
                background-color: #F3F4F6;
                color: #111827;
                border: 1px solid #D1D5DB;
                padding: 6px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
            }
            """)

        self.setWindowFlag(
            Qt.WindowType.WindowStaysOnTopHint,
            True
        )

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
        self.table.setColumnCount(3)

        self.table.setHorizontalHeaderLabels([
            "Ветка",
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

        table_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        for row_index, device in enumerate(devices):
            _, name, ip, path = device

            path_item = QTableWidgetItem(path if path else "")
            name_item = QTableWidgetItem(name)
            ip_item = QTableWidgetItem(ip if ip else "")

            name_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            ip_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            path_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.table.setItem(
                row_index,
                0,
                path_item
            )

            self.table.setItem(
                row_index,
                1,
                name_item
            )

            self.table.setItem(
                row_index,
                2,
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

    def __init__(self, parent):
        self.parent = parent

        self.tray_icon = QSystemTrayIcon(parent)

        icon = QIcon(
            resource_path("icons/icon-monitor.png")
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
            ip,
            device_path=None):

        self.pending_offline_devices.append(
            (
                device_id,
                name,
                ip,
                device_path
            )
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
            _, name, ip, path = devices[0]

            if path:
                return (
                    f"{path}\n"
                    f"{ip}\n"
                    f"Потеряна связь"
                )

            return (
                f"{name}\n"
                f"{ip}\n"
                f"Потеряна связь"
            )

        lines = []

        for _, name, ip, path in devices:
            if path:
                lines.append(
                    f"• {path} — {ip}"
                )
            else:
                lines.append(
                    f"• {name} — {ip}"
                )

        return "\n".join(lines)

    def show_popup(
            self,
            title,
            devices,
            device_ids):

        current_theme = self.parent.db.get_setting(
            "theme",
            "light"
        )

        dialog = OfflineDevicesDialog(
            title,
            devices,
            dark_theme=(current_theme == "dark"),
            parent=self.parent
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
        dialog.raise_()
        dialog.activateWindow()

    def device_online(
            self,
            device_id,
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