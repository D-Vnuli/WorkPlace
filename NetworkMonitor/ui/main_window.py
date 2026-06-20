import os
import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
import subprocess
from ui.styles import LIGHT_STYLE, DARK_STYLE
import webbrowser
from PyQt6.QtWidgets import QHeaderView
from datetime import datetime
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QInputDialog,
    QMessageBox,
    QLabel,
    QFileDialog,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QMenu,
    QAbstractItemView,
    QSystemTrayIcon,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox
)
from database import Database
from ping_worker import PingWorker
from notifications import NotificationManager
from PyQt6.QtWidgets import QFileDialog
from config_manager import set_database_path, get_database_path, export_database


OFFLINE_DELAY_SECONDS = 60


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class DeviceTreeWidget(QTreeWidget):
    device_moved = pyqtSignal(int, object)

    def dropEvent(self, event):
        moved_item = self.currentItem()

        if not moved_item:
            super().dropEvent(event)
            return

        device_id = moved_item.data(0, Qt.ItemDataRole.UserRole)

        super().dropEvent(event)

        new_parent = moved_item.parent()

        if new_parent:
            parent_id = new_parent.data(0, Qt.ItemDataRole.UserRole)
        else:
            parent_id = None

        self.device_moved.emit(device_id, parent_id)


class DevicePropertiesDialog(QDialog):

    def __init__(
            self,
            name,
            ip,
            device_type,
            status,
            last_seen,
            dark_theme=False,
            parent=None):

        super().__init__(parent)

        self.setWindowTitle("Свойства")
        if dark_theme:
            self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                color: #F3F4F6;
            }

            QLabel {
                color: #F3F4F6;
            }

            QLineEdit {
                background-color: #1E1E1E;
                color: #F3F4F6;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 6px;
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

            QLineEdit {
                background-color: #FFFFFF;
                color: #111827;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
            }
            """)

        layout = QFormLayout(self)

        self.name_input = QLineEdit(name)
        self.ip_input = QLineEdit(ip if ip else "")

        layout.addRow(
            "Название:",
            self.name_input
        )

        if device_type != "group":

            layout.addRow(
                "IP адрес:",
                self.ip_input
            )

        else:

            self.ip_input.setEnabled(False)

        lbl_status = QLabel(
            status if status else "unknown"
        )

        if last_seen:

            try:

                from datetime import datetime

                dt = datetime.strptime(
                    last_seen,
                    "%Y-%m-%d %H:%M:%S"
                )

                last_seen = dt.strftime(
                    "%H:%M %d-%m-%Y"
                )

            except Exception:
                pass

        lbl_last_seen = QLabel(
            last_seen if last_seen else "Нет данных"
        )

        layout.addRow(
            "Статус:",
            lbl_status
        )

        layout.addRow(
            "Последний ответ:",
            lbl_last_seen
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)



    def get_data(self):

        return (
            self.name_input.text().strip(),
            self.ip_input.text().strip()
        )


class TextInputDialog(QDialog):

    def __init__(
            self,
            title,
            label_text,
            dark_theme=False,
            parent=None):

        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(350, 150)

        if dark_theme:
            bg_color = "#252526"
            text_color = "#F3F4F6"
            input_bg = "#1E1E1E"
            border = "#3F3F46"
        else:
            bg_color = "#FFFFFF"
            text_color = "#111827"
            input_bg = "#FFFFFF"
            border = "#D1D5DB"

        self.setStyleSheet(f"""
        QDialog {{
            background-color: {bg_color};
        }}

        QLabel {{
            color: {text_color};
        }}

        QLineEdit {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 6px;
        }}

        QPushButton {{
            background-color: #2563EB;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 7px 12px;
        }}
        """)

        layout = QVBoxLayout(self)

        label = QLabel(label_text)

        self.edit = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(label)
        layout.addWidget(self.edit)
        layout.addWidget(buttons)

    def get_text(self):
        return self.edit.text().strip()

class MainWindow(QMainWindow):

    def show_warning_message(self, title, text):
        current_theme = self.db.get_setting("theme", "light")

        if current_theme == "dark":
            bg_color = "#1E1E1E"
            text_color = "#F3F4F6"
            table_bg = "#252526"
            border_color = "#3F3F46"
        else:
            bg_color = "#FFFFFF"
            text_color = "#111827"
            table_bg = "#F9FAFB"
            border_color = "#D1D5DB"

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(450, 210)

        dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {bg_color};
        }}

        QLabel {{
            color: {text_color};
            background: transparent;
        }}

        QPushButton {{
            background-color: #2563EB;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 7px 12px;
            min-width: 110px;
        }}
        """)

        layout = QVBoxLayout(dialog)

        header_layout = QVBoxLayout()

        icon_label = QLabel("⚠")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 28px;
            color: #FACC15;
        """)

        title_label = QLabel("Ошибка")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #DC2626;
        """)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)

        message_box = QLabel(text)
        message_box.setWordWrap(True)
        message_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_box.setStyleSheet(f"""
            background-color: {table_bg};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 8px;
            color: {text_color};
        """)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)

        layout.addLayout(header_layout)
        layout.addSpacing(4)
        layout.addWidget(message_box)
        layout.addSpacing(4)
        layout.addLayout(button_layout)

        dialog.exec()

    def input_text(self, title, label):

        current_theme = self.db.get_setting(
            "theme",
            "light"
        )

        dialog = TextInputDialog(
            title,
            label,
            dark_theme=(current_theme == "dark"),
            parent=self
        )

        result = dialog.exec()

        return (
            dialog.get_text(),
            result == QDialog.DialogCode.Accepted
        )

    def get_app_dir(self):
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    def check_update_flag(self):
        flag_path = os.path.join(self.get_app_dir(), "update.flag")

        if os.path.exists(flag_path):
            self.exit_for_update()

    def exit_for_update(self):
        # Останавливаем таймер проверки обновления
        if hasattr(self, "update_timer"):
            self.update_timer.stop()

        # Останавливаем ping worker
        if hasattr(self, "ping_worker") and self.ping_worker:
            self.ping_worker.stop()
            self.ping_worker.wait()

        if hasattr(self, "notifications"):
            self.notifications.tray_icon.hide()

        QApplication.quit()

    def change_theme(self, theme_name):
        print("Тема изменена:", theme_name)

        if theme_name == "Тёмная":
            QApplication.instance().setStyleSheet(DARK_STYLE)
            self.db.set_setting("theme", "dark")
        else:
            QApplication.instance().setStyleSheet(LIGHT_STYLE)
            self.db.set_setting("theme", "light")

        self.load_devices()

    def __init__(self):
        super().__init__()

        self.db = Database()
        self.properties_window_open = False
        self.notifications = NotificationManager(self)
        self.pending_offline = {}
        self.force_exit = False
        self.devices_refresh_pending = False
        self.events_refresh_pending = False

        self.devices_refresh_timer = QTimer(self)
        self.devices_refresh_timer.setSingleShot(True)
        self.devices_refresh_timer.timeout.connect(self.load_devices)

        self.events_refresh_timer = QTimer(self)
        self.events_refresh_timer.setSingleShot(True)
        self.events_refresh_timer.timeout.connect(self.load_events)

        self.shared_db_refresh_timer = QTimer(self)
        self.shared_db_refresh_timer.timeout.connect(self.refresh_from_shared_db)
        self.shared_db_refresh_timer.start(30 * 1000)  # обновление общей базы раз в 30 секунд

        self.setWindowTitle("Network Monitor")
        app_icon = QIcon(resource_path("icons/icon-monitor.png"))
        self.setWindowIcon(app_icon)

        self.setup_ui()
        self.setup_tray_menu()
        self.restore_window_settings()
        self.load_devices()
        self.load_events()
        self.show_startup_offline_notifications()

        self.ping_worker = PingWorker()

        self.ping_worker.device_status_changed.connect(
            self.on_device_status_changed
        )

        self.refresh_ping_worker()
        self.ping_worker.start()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_update_flag)
        self.update_timer.start(60000)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()

        self.btn_add_group = QPushButton("Добавить группу")
        self.btn_add_device = QPushButton("Добавить устройство")

        self.lbl_online = QLabel("🟢 В сети: 0")
        self.lbl_offline = QLabel("🔴 Не в сети: 0")

        top_layout.addWidget(self.btn_add_group)
        top_layout.addWidget(self.btn_add_device)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_online)
        top_layout.addWidget(self.lbl_offline)

        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        devices_tab = QWidget()
        devices_layout = QVBoxLayout(devices_tab)

        self.tree = DeviceTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(22)

        self.tree.setHeaderLabels([
            "Устройство",
            "IP адрес",
            "Состояние"
        ])

        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(28)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove
        )
        self.tree.setDefaultDropAction(
            Qt.DropAction.MoveAction
        )

        devices_layout.addWidget(self.tree)
        header = self.tree.header()

        header.setStretchLastSection(False)
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed
        )

        self.tree.setColumnWidth(1, 160)
        self.tree.setColumnWidth(2, 140)
        self.tabs.addTab(devices_tab, "Устройства")

        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        self.btn_clear_log = QPushButton("Очистить журнал")
        self.btn_clear_log.clicked.connect(self.clear_log)

        log_layout.addWidget(self.btn_clear_log)

        self.log_table = QTableWidget()

        self.log_table.setColumnCount(4)

        self.log_table.setAlternatingRowColors(True)
        self.log_table.setShowGrid(True)

        self.log_table.setHorizontalHeaderLabels([
            "Время",
            "Устройство",
            "IP",
            "Событие"
        ])

        self.log_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.log_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        header = self.log_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        self.log_table.setColumnWidth(0, 140)
        self.log_table.setColumnWidth(2, 150)

        self.log_table.verticalHeader().setVisible(False)

        log_layout.addWidget(self.log_table)
        self.tabs.addTab(log_tab, "Журнал")
        database_tab = QWidget()
        database_layout = QVBoxLayout(database_tab)

        self.lbl_database_path = QLabel(
            f"Текущая база данных:\n{get_database_path()}"
        )

        self.lbl_database_path.setWordWrap(True)

        self.btn_select_db = QPushButton("Выбрать базу")
        self.btn_save_db = QPushButton("Сохранить базу")

        self.btn_select_db.setFixedWidth(180)
        self.btn_save_db.setFixedWidth(180)

        self.cmb_theme = QComboBox()

        self.cmb_theme.addItems([
            "Светлая",
            "Тёмная"
        ])
        saved_theme = self.db.get_setting(
            "theme",
            "light"
        )

        if saved_theme == "dark":
            self.cmb_theme.setCurrentText("Тёмная")
        else:
            self.cmb_theme.setCurrentText("Светлая")
        self.cmb_theme.currentTextChanged.connect(
            self.change_theme
        )
        self.cmb_theme.setFixedWidth(180)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_select_db)
        buttons_layout.addWidget(self.btn_save_db)
        buttons_layout.addStretch()

        database_layout.addWidget(self.lbl_database_path)
        database_layout.addLayout(buttons_layout)

        database_layout.addSpacing(20)

        database_layout.addWidget(
            QLabel("Тема оформления")
        )

        database_layout.addWidget(
            self.cmb_theme
        )

        database_layout.addStretch()

        self.btn_about = QPushButton("О программе")
        self.btn_about.setFixedWidth(180)
        self.btn_about.clicked.connect(self.show_about_program)

        database_layout.addWidget(self.btn_about)

        self.tabs.addTab(database_tab, "Настройки")

        self.btn_select_db.clicked.connect(
            self.select_database
        )

        self.btn_save_db.clicked.connect(
            self.save_database_file
        )
        self.btn_add_group.clicked.connect(self.add_group)
        self.btn_add_device.clicked.connect(self.add_device)

        self.tree.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.tree.customContextMenuRequested.connect(
            self.show_context_menu
        )

        self.tree.device_moved.connect(
            self.on_device_moved
        )

    def setup_tray_menu(self):
        tray_menu = QMenu(self)

        open_action = tray_menu.addAction("Открыть")
        exit_action = tray_menu.addAction("Выход")

        open_action.triggered.connect(self.restore_from_tray)
        exit_action.triggered.connect(self.exit_application)

        tray_icon = QIcon(resource_path("icons/icon-monitor.png"))

        self.notifications.tray_icon.setIcon(tray_icon)
        self.notifications.tray_icon.setToolTip("Network Monitor")
        self.notifications.tray_icon.setContextMenu(tray_menu)
        self.notifications.tray_icon.show()

        self.notifications.tray_icon.activated.connect(
            self.on_tray_activated
        )

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_from_tray()

    def restore_from_tray(self):
        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def exit_application(self):
        self.force_exit = True

        self.save_expanded_items()
        self.save_window_settings()

        if hasattr(self, "ping_worker"):
            self.ping_worker.stop()
            self.ping_worker.wait()

        if hasattr(self, "notifications"):
            self.notifications.tray_icon.hide()

        QApplication.quit()

    def show_startup_offline_notifications(self):
        devices = self.db.get_unacknowledged_offline_devices()

        for device in devices:
            device_id = device[0]
            name = device[1]
            ip = device[2]

            self.notifications.device_offline(
                device_id,
                name,
                ip
            )

    def restore_window_settings(self):
        width = int(self.db.get_setting("window_width", 1000))
        height = int(self.db.get_setting("window_height", 700))

        self.resize(width, height)

        self.tree.setColumnWidth(
            0,
            int(self.db.get_setting("tree_column_0_width", 350))
        )

        self.tree.setColumnWidth(
            1,
            int(self.db.get_setting("tree_column_1_width", 160))
        )

        self.tree.setColumnWidth(
            2,
            int(self.db.get_setting("tree_column_2_width", 120))
        )

    def save_window_settings(self):
        self.db.set_setting("window_width", str(self.width()))
        self.db.set_setting("window_height", str(self.height()))
        self.db.set_setting("tree_column_0_width", str(self.tree.columnWidth(0)))
        self.db.set_setting("tree_column_1_width", str(self.tree.columnWidth(1)))
        self.db.set_setting("tree_column_2_width", str(self.tree.columnWidth(2)))

    def get_expanded_items(self):
        expanded = set()

        def walk(item):
            device_id = item.data(0, Qt.ItemDataRole.UserRole)

            if item.isExpanded():
                expanded.add(device_id)

            for index in range(item.childCount()):
                walk(item.child(index))

        for index in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(index))

        return expanded

    def save_expanded_items(self):
        expanded_items = self.get_expanded_items()

        value = ",".join(
            str(device_id)
            for device_id in expanded_items
        )

        self.db.set_setting(
            "expanded_items",
            value
        )

    def get_saved_expanded_items(self):
        value = self.db.get_setting(
            "expanded_items",
            ""
        )

        if not value:
            return set()

        return set(
            int(item)
            for item in value.split(",")
            if item.strip().isdigit()
        )

    def load_events(self):
        events = self.db.get_events()

        self.log_table.setRowCount(len(events))

        for row_index, row in enumerate(events):
            timestamp = row[0]
            try:

                dt = datetime.strptime(
                    timestamp,
                    "%Y-%m-%d %H:%M:%S"
                )

                timestamp = dt.strftime(
                    "%H:%M %d-%m-%Y"
                )

            except Exception:
                pass
            device_name = row[1]
            ip = row[2]
            event = row[3]

            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            device_item = QTableWidgetItem(device_name)
            device_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            ip_item = QTableWidgetItem(
                ip if ip else ""
            )
            ip_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            event_item = QTableWidgetItem(event)
            event_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.log_table.setItem(
                row_index,
                0,
                time_item
            )

            self.log_table.setItem(
                row_index,
                1,
                device_item
            )

            self.log_table.setItem(
                row_index,
                2,
                ip_item
            )

            self.log_table.setItem(
                row_index,
                3,
                event_item
            )

    def clear_log(self):
        result = QMessageBox.question(
            self,
            "Очистка журнала",
            "Вы действительно хотите очистить журнал событий?"
        )

        if result == QMessageBox.StandardButton.Yes:
            self.db.clear_events()
            self.load_events()

    def add_event_to_log(self, device_name, ip, event_text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.add_event(
            timestamp,
            device_name,
            ip,
            event_text
        )

        self.add_event_row_to_table(
            timestamp,
            device_name,
            ip,
            event_text
        )

    def add_event_row_to_table(self, timestamp, device_name, ip, event_text):
        try:
            dt = datetime.strptime(
                timestamp,
                "%Y-%m-%d %H:%M:%S"
            )

            timestamp = dt.strftime(
                "%H:%M %d-%m-%Y"
            )

        except Exception:
            pass

        row_index = self.log_table.rowCount()
        self.log_table.insertRow(row_index)

        time_item = QTableWidgetItem(timestamp)
        time_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        device_item = QTableWidgetItem(device_name)
        device_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        ip_item = QTableWidgetItem(
            ip if ip else ""
        )
        ip_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        event_item = QTableWidgetItem(event_text)
        event_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.log_table.setItem(
            row_index,
            0,
            time_item
        )

        self.log_table.setItem(
            row_index,
            1,
            device_item
        )

        self.log_table.setItem(
            row_index,
            2,
            ip_item
        )

        self.log_table.setItem(
            row_index,
            3,
            event_item
        )

    def on_device_moved(self, device_id, parent_id):
        self.db.update_device_parent(
            device_id,
            parent_id
        )

        self.load_devices()

    def request_devices_refresh(self):
        if self.devices_refresh_timer.isActive():
            return

        self.devices_refresh_timer.start(1500)

    def request_events_refresh(self):
        if self.events_refresh_timer.isActive():
            return

        self.events_refresh_timer.start(1500)

    def refresh_from_shared_db(self):
        if self.properties_window_open:
            return

        self.load_devices()
        self.load_events()

    def refresh_ping_worker(self, devices=None):
        if not hasattr(self, "ping_worker"):
            return

        if devices is None:
            devices = self.db.get_devices()

        ping_devices = []

        for row in devices:
            device_id = row[0]
            ip = row[3]
            device_type = row[4]

            if device_type == "group":
                continue

            if not ip:
                continue

            ping_devices.append((device_id, ip))

        self.ping_worker.update_devices(ping_devices)

    def on_device_status_changed(self, device_id, new_status):
        device = self.db.get_device_by_id(device_id)

        if not device:
            return

        device_name = device[2]
        ip = device[3]
        old_status = device[5]

        now = datetime.now()

        if new_status == "online":

            self.db.update_last_seen_if_needed(
                device_id,
                seconds=60
            )

            if device_id in self.pending_offline:
                del self.pending_offline[device_id]

            if old_status != "online":
                self.db.update_status(
                    device_id,
                    "online"
                )

                if old_status == "offline":
                    self.add_event_to_log(
                        device_name,
                        ip,
                        "Связь восстановлена"
                    )

                    device_path = self.db.get_device_path(device_id)

                    self.notifications.device_online(
                        device_id,
                        device_name,
                        ip,
                        device_path
                    )

                if not self.properties_window_open:
                    self.request_devices_refresh()

            return

        if new_status == "offline":
            if old_status == "offline":
                return

            if device_id not in self.pending_offline:
                self.pending_offline[device_id] = now
                return

            first_loss_time = self.pending_offline[device_id]

            seconds_offline = (
                    now - first_loss_time
            ).total_seconds()

            if seconds_offline < OFFLINE_DELAY_SECONDS:
                return

            self.db.update_status(
                device_id,
                "offline"
            )

            if device_id in self.pending_offline:
                del self.pending_offline[device_id]

            self.add_event_to_log(
                device_name,
                ip,
                "Устройство недоступно"
            )

            device_path = self.db.get_device_path(device_id)

            self.notifications.device_offline(
                device_id,
                device_name,
                ip,
                device_path
            )

            self.request_devices_refresh()

    def update_counters(self, devices):
        online = 0
        offline = 0

        for row in devices:
            device_type = row[4]
            status = row[5]

            if device_type == "group":
                continue

            if status == "online":
                online += 1
            elif status == "offline":
                offline += 1

        self.lbl_online.setText(f"🟢 В сети: {online}")
        self.lbl_offline.setText(f"🔴 Не в сети: {offline}")

    def show_about_program(self):
        dialog = QDialog(self)

        current_theme = self.db.get_setting(
            "theme",
            "light"
        )

        if current_theme == "dark":
            bg_color = "#252526"
            text_color = "#F3F4F6"
        else:
            bg_color = "#FFFFFF"
            text_color = "#111827"

        dialog.setWindowTitle("О программе")
        dialog.setWindowIcon(
            QIcon(resource_path("icons/icon-monitor.png"))
        )
        dialog.setFixedSize(450, 280)

        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
            }}

            QLabel {{
                color: {text_color};
                background: transparent;
            }}

            QPushButton {{
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
            }}

            QPushButton:hover {{
                background-color: #1D4ED8;
            }}
        """)

        layout = QVBoxLayout(dialog)

        title = QLabel("Network Monitor")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 18pt;
            font-weight: bold;
            color: {text_color};
            background: transparent;
        """)

        description = QLabel(
            "Программа для мониторинга сетевых устройств"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        contacts = QLabel(
            f"""
            <a href="https://t.me/DenisVnuli"
               style="color:{text_color}; text-decoration:none;">
               Telegram: @DenisVnuli
            </a>
            <br><br>
            <span style="color:{text_color};">
                d.stronsky.ai@gmail.com
            </span>
            """
        )
        contacts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contacts.setOpenExternalLinks(True)

        version = QLabel("Версия 2.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(contacts)
        layout.addSpacing(20)
        layout.addWidget(version)
        layout.addStretch()
        layout.addWidget(btn_ok)

        dialog.exec()

    def select_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать базу данных",
            "",
            "SQLite Database (*.db);;All Files (*)"
        )

        if not file_path:
            return

        set_database_path(file_path)

        self.lbl_database_path.setText(
            f"Текущая база данных:\n{file_path}"
        )

        QMessageBox.information(
            self,
            "База данных",
            "Путь к базе сохранён. Перезапустите программу."
        )

    def save_database_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить базу данных как",
            "network_monitor.db",
            "SQLite Database (*.db);;All Files (*)"
        )

        if not file_path:
            return

        try:
            export_database(file_path)

            QMessageBox.information(
                self,
                "Сохранение базы",
                "База данных успешно сохранена."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить базу:\n{error}"
            )

    def add_group(self):
        name, ok = self.input_text(
            "Группа",
            "Название группы:"
        )

        if not ok or not name:
            return

        parent_id = None
        current = self.tree.currentItem()

        if current:
            parent_id = current.data(0, Qt.ItemDataRole.UserRole)

        self.db.add_device(
            name=name,
            ip="",
            device_type="group",
            parent_id=parent_id
        )

        self.load_devices()

    def add_device(self):
        name, ok = self.input_text(
            "Устройство",
            "Название устройства:"
        )

        if not ok or not name:
            return

        ip, ok = self.input_text(
            "IP адрес",
            "Введите IP:"
        )

        if not ok or not ip:
            return

        existing_device = self.db.ip_exists(ip)

        if existing_device:
            existing_id, existing_name = existing_device

            self.show_warning_message(
                "Дубликат IP адреса",
                f"Устройство с IP адресом {ip} уже добавлено:\n\nУстройство: {existing_name}"
            )

            return

        parent_id = None
        current = self.tree.currentItem()

        if current:
            parent_id = current.data(0, Qt.ItemDataRole.UserRole)

        self.db.add_device(
            name=name,
            ip=ip,
            device_type="device",
            parent_id=parent_id
        )

        self.load_devices()

    def edit_properties(self):
        item = self.tree.currentItem()

        if not item:
            return

        device_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        device = self.db.get_device_by_id(device_id)

        if not device:
            return

        name = device[2]
        ip = device[3]
        device_type = device[4]
        status = device[5]
        last_seen = device[6]

        current_theme = self.db.get_setting(
            "theme",
            "light"
        )

        dialog = DevicePropertiesDialog(
            name,
            ip,
            device_type,
            status,
            last_seen,
            dark_theme=(current_theme == "dark"),
            parent=self
        )

        self.properties_window_open = True

        result = dialog.exec()

        self.properties_window_open = False

        if result != QDialog.DialogCode.Accepted:
            self.load_devices()
            return

        new_name, new_ip = dialog.get_data()

        if not new_name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Название не может быть пустым."
            )

            self.load_devices()
            return

        if device_type == "group":
            new_ip = ""

        if device_type != "group":
            existing_device = self.db.ip_exists(
                new_ip,
                exclude_device_id=device_id
            )

            if existing_device:
                existing_id, existing_name = existing_device

                self.show_warning_message(
                    "Дубликат IP адреса",
                    f"Устройство с IP адресом {ip} уже добавлено:\n\nУстройство: {existing_name}"
                )

                self.load_devices()
                return

        self.db.update_device(
            device_id,
            new_name,
            new_ip
        )

        self.load_devices()

    def open_web_interface(self, protocol):
        item = self.tree.currentItem()

        if not item:
            return

        ip = item.text(1).strip()

        if not ip:
            QMessageBox.warning(
                self,
                "Ошибка",
                "У выбранного элемента нет IP адреса."
            )
            return

        url = f"{protocol}://{ip}"

        webbrowser.open(url)

    def ping_in_cmd(self):
        item = self.tree.currentItem()

        if not item:
            return

        ip = item.text(1).strip()

        if not ip:
            QMessageBox.warning(
                self,
                "Ошибка",
                "У выбранного элемента нет IP адреса."
            )
            return

        subprocess.Popen(
            [
                "cmd",
                "/k",
                "ping",
                "-t",
                ip
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def rename_item(self):
        item = self.tree.currentItem()

        if not item:
            return

        device_id = item.data(0, Qt.ItemDataRole.UserRole)

        new_name, ok = self.input_text(
            "Переименование",
            "Новое название:"
        )

        if not ok or not new_name:
            return

        self.db.update_device_name(
            device_id,
            new_name
        )

        self.load_devices()

    def delete_item(self):
        item = self.tree.currentItem()

        if not item:
            return

        device_id = item.data(0, Qt.ItemDataRole.UserRole)

        msg = QMessageBox(self)

        msg.setWindowTitle("Удаление")
        msg.setText("Удалить выбранную ветку?")

        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        current_theme = self.db.get_setting(
            "theme",
            "light"
        )

        if current_theme == "dark":

            msg.setStyleSheet("""
            QMessageBox {
                background-color: #252526;
                color: #F3F4F6;
            }

            QLabel {
                color: #F3F4F6;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                min-width: 80px;
            }
            """)

        else:

            msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #111827;
            }

            QLabel {
                color: #111827;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                min-width: 80px;
            }
            """)

        result = msg.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.db.delete_branch(device_id)

            if device_id in self.pending_offline:
                del self.pending_offline[device_id]

            self.load_devices()

    def copy_name(self):
        item = self.tree.currentItem()

        if item:
            QApplication.clipboard().setText(
                item.text(0)
            )

    def copy_ip(self):
        item = self.tree.currentItem()

        if item:
            QApplication.clipboard().setText(
                item.text(1)
            )

    def show_context_menu(self, position):
        menu = QMenu(self)

        add_group_action = menu.addAction("Добавить группу")
        add_device_action = menu.addAction("Добавить устройство")

        menu.addSeparator()

        properties_action = menu.addAction("Свойства")

        web_menu = menu.addMenu("Web")
        web_http_action = web_menu.addAction("HTTP")
        web_https_action = web_menu.addAction("HTTPS")

        ping_cmd_action = menu.addAction("Проверить CMD")
        delete_action = menu.addAction("Удалить")

        menu.addSeparator()

        action = menu.exec(
            self.tree.viewport().mapToGlobal(position)
        )

        if action == add_group_action:
            self.add_group()

        elif action == add_device_action:
            self.add_device()

        elif action == properties_action:
            self.edit_properties()

        elif action == web_http_action:
            self.open_web_interface("http")

        elif action == web_https_action:
            self.open_web_interface("https")

        elif action == ping_cmd_action:
            self.ping_in_cmd()

        elif action == delete_action:
            self.delete_item()

    def load_devices(self):
        expanded_items = self.get_expanded_items()

        if not expanded_items:
            expanded_items = self.get_saved_expanded_items()

        self.tree.clear()

        devices = self.db.get_devices()
        current_theme = self.db.get_setting(
            "theme",
            "light"
        )
        items = {}

        offline_by_parent = {}

        parent_map = {}

        for row in devices:
            device_id = row[0]
            parent_id = row[1]

            parent_map[device_id] = parent_id

        def mark_parent_offline(parent_id):
            while parent_id:
                offline_by_parent[parent_id] = True
                parent_id = parent_map.get(parent_id)

        for row in devices:
            parent_id = row[1]
            device_type = row[4]
            status = row[5]

            if device_type != "group" and status == "offline":
                mark_parent_offline(parent_id)

        for row in devices:
            device_id = row[0]
            parent_id = row[1]
            name = row[2]
            ip = row[3]
            device_type = row[4]
            status = row[5]

            if device_type == "group":
                if offline_by_parent.get(device_id):
                    display_name = f"⚠️  📁 {name}"
                else:
                    display_name = f"📁  {name}"

                item = QTreeWidgetItem([
                    display_name,
                    "",
                    ""
                ])


            else:

                if status == "online":

                    display_status = "● В сети"

                elif status == "offline":

                    display_status = "● Не в сети"

                else:

                    display_status = "● Нет данных"

                if status == "offline":

                    display_name = f"⚠️  {name}"


                elif offline_by_parent.get(device_id):

                    display_name = f"⚠️  {name}"


                else:

                    display_name = f"  {name}"

                item = QTreeWidgetItem([

                    display_name,

                    ip if ip else "",

                    display_status

                ])

            if device_type == "group":
                font = item.font(0)
                font.setBold(True)

                item.setFont(0, font)

                if current_theme == "dark":

                    if offline_by_parent.get(device_id):
                        item.setForeground(0, QColor("#FCA5A5"))

                        item.setBackground(0, QColor("#3A2525"))
                        item.setBackground(1, QColor("#3A2525"))
                        item.setBackground(2, QColor("#3A2525"))


                    else:

                        item.setForeground(0, QColor("#F3F4F6"))

                else:

                    if offline_by_parent.get(device_id):
                        item.setForeground(0, QColor("#DC2626"))

                        item.setBackground(0, QColor("#FEF2F2"))
                        item.setBackground(1, QColor("#FEF2F2"))
                        item.setBackground(2, QColor("#FEF2F2"))

                    else:

                        item.setForeground(0, QColor("#111827"))

            elif status == "online":
                item.setForeground(2, QColor("#16A34A"))

            elif status == "offline":
                item.setForeground(2, QColor("#DC2626"))

            else:
                item.setForeground(2, QColor("#6B7280"))

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                device_id
            )

            items[device_id] = (
                item,
                parent_id
            )

        for device_id, data in items.items():
            item = data[0]
            parent_id = data[1]

            if parent_id and parent_id in items:
                parent_item = items[parent_id][0]
                parent_item.addChild(item)

            else:
                self.tree.addTopLevelItem(item)

        for device_id, data in items.items():
            item = data[0]

            if device_id in expanded_items:
                item.setExpanded(True)

        self.update_counters(devices)

        if hasattr(self, "ping_worker"):
            self.refresh_ping_worker(devices)

    def closeEvent(self, event):
        self.save_expanded_items()
        self.save_window_settings()

        if self.force_exit:
            if hasattr(self, "ping_worker"):
                self.ping_worker.stop()
                self.ping_worker.wait()

            if hasattr(self, "notifications"):
                self.notifications.tray_icon.hide()

            event.accept()

        else:
            event.ignore()
            self.hide()

            if hasattr(self, "notifications"):
                self.notifications.tray_icon.show()
                self.notifications.tray_icon.showMessage(
                    "Network Monitor",
                    "Программа свернута в трей",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )