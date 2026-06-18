import sys
import winreg
from pathlib import Path


APP_NAME = "NetworkMonitor"

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_app_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    main_path = Path(__file__).resolve().parent / "main.py"
    return f'"{sys.executable}" "{main_path}"'


def enable_autostart():
    command = get_app_command()

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY,
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            command
        )


def disable_autostart():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass


def is_autostart_enabled():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)

        return value == get_app_command()

    except FileNotFoundError:
        return False