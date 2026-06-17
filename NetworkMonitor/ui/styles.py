APP_STYLE = """
QMainWindow {
    background-color: #F4F6F8;
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
"""