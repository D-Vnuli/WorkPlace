LIGHT_STYLE = """
QMainWindow {
    background-color: #F4F6F8;
}
QDialog {
    background-color: #252526;
    color: white;
}

QMessageBox {
    background-color: #252526;
    color: white;
}

QCheckBox {
    color: white;
}

QComboBox {
    background-color: #2D2D30;
    color: white;
    border: 1px solid #3A3A3A;
    padding: 4px;
}

QComboBox QAbstractItemView {
    background-color: #2D2D30;
    color: white;
    selection-background-color: #3E6AE1;
}

QTableCornerButton::section {
    background-color: #2D2D30;
    border: 1px solid #3A3A3A;
}

QWidget {
    font-family: Segoe UI;
    font-size: 10pt;
}

QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QLabel {
    color: #1F2937;
}

QTabWidget::pane {
    border: 1px solid #D1D5DB;
    background: white;
    border-radius: 6px;
}

QTabBar::tab {
    background: #E5E7EB;
    color: #374151;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: white;
    color: #111827;
    font-weight: bold;
}

QTreeWidget,
QTableWidget {
    background-color: white;
    alternate-background-color: #F9FAFB;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    gridline-color: #E5E7EB;
    selection-background-color: #DBEAFE;
    selection-color: #111827;
}

QHeaderView::section {
    background-color: #F3F4F6;
    color: #374151;
    border: none;
    border-bottom: 1px solid #D1D5DB;
    padding: 6px;
    font-weight: bold;
}

QLineEdit {
    background-color: white;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px;
}

QMenu {
    background-color: white;
    border: 1px solid #D1D5DB;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
}

QMenu::item:selected {
    background-color: #DBEAFE;
}
QComboBox {
    background-color: white;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px;
}

QComboBox QAbstractItemView {
    background-color: white;
    color: #111827;
    selection-background-color: #DBEAFE;
    selection-color: #111827;
}

QCheckBox {
    color: #111827;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
}
"""

DARK_STYLE = """
QMainWindow {
    background-color: #1E1E1E;
}

QWidget {
    font-family: Segoe UI;
    font-size: 10pt;
    color: #F3F4F6;
    background-color: #1E1E1E;
}

QDialog,
QMessageBox {
    background-color: #252526;
    color: #F3F4F6;
}

QMessageBox QLabel {
    color: #F3F4F6;
    background: transparent;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QLabel {
    color: #F3F4F6;
    background: transparent;
}

QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QTabWidget::pane {
    border: 1px solid #3A3A3A;
    background: #252526;
    border-radius: 6px;
}

QTabBar::tab {
    background: #2D2D30;
    color: #D4D4D4;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #252526;
    color: white;
    font-weight: bold;
}

QTreeWidget,
QTableWidget {
    background-color: #252526;
    alternate-background-color: #2D2D30;
    color: #F3F4F6;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    gridline-color: #3A3A3A;
    selection-background-color: #1F4E79;
    selection-color: white;
}

QTreeWidget::item:selected,
QTableWidget::item:selected {
    background-color: #1F4E79;
    color: white;
}

QHeaderView::section {
    background-color: #2D2D30;
    color: #F3F4F6;
    border: none;
    border-bottom: 1px solid #3A3A3A;
    padding: 6px;
    font-weight: bold;
}

QLineEdit {
    background-color: #2D2D30;
    color: #F3F4F6;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    padding: 6px;
}

QComboBox {
    background-color: #2D2D30;
    color: #F3F4F6;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    padding: 6px;
}

QComboBox QAbstractItemView {
    background-color: #2D2D30;
    color: #F3F4F6;
    border: 1px solid #3A3A3A;
    selection-background-color: #2563EB;
    selection-color: white;
}

QCheckBox {
    color: #F3F4F6;
    background: transparent;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    background-color: #F3F4F6;
    border: 1px solid #9CA3AF;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border: 1px solid #2563EB;
}

QMenu {
    background-color: #2D2D30;
    color: #F3F4F6;
    border: 1px solid #3A3A3A;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
}

QMenu::item:selected {
    background-color: #2563EB;
    color: white;
}

QTableCornerButton::section {
    background-color: #2D2D30;
    border: 1px solid #3A3A3A;
}

QScrollBar:vertical {
    background: #252526;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #4B5563;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #6B7280;
}

QScrollBar:horizontal {
    background: #252526;
    height: 12px;
}

QScrollBar::handle:horizontal {
    background: #4B5563;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #6B7280;
}
"""