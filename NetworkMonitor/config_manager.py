import json
import shutil
import sys
from pathlib import Path


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent


CONFIG_PATH = get_app_dir() / "config.json"
DEFAULT_DB_PATH = get_app_dir() / "network_monitor.db"


def load_config():
    if not CONFIG_PATH.exists():
        return {
            "database_path": str(DEFAULT_DB_PATH)
        }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {
            "database_path": str(DEFAULT_DB_PATH)
        }


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)


def get_database_path():
    config = load_config()
    return Path(config.get("database_path", str(DEFAULT_DB_PATH)))


def set_database_path(path):
    config = load_config()
    config["database_path"] = str(path)
    save_config(config)


def export_database(destination_path):
    source_path = get_database_path()

    if not source_path.exists():
        raise FileNotFoundError("Текущая база данных не найдена.")

    shutil.copy2(source_path, destination_path)