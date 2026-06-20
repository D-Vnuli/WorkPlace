import sqlite3
from config_manager import get_database_path

DB_PATH = get_database_path()

class Database:

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(
            DB_PATH,
            timeout=10
        )

        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 10000")
        self.conn.execute("PRAGMA synchronous = NORMAL")

        self.create_tables()
        self.migrate_tables()

    def update_last_seen(self, device_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET last_seen = datetime('now', 'localtime')
        WHERE id = ?
        """, (device_id,))

        self.conn.commit()

    def update_last_seen_if_needed(self, device_id, seconds=60):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET last_seen = datetime('now', 'localtime')
        WHERE id = ?
          AND (
              last_seen IS NULL
              OR datetime(last_seen) <= datetime('now', 'localtime', ?)
          )
        """, (
            device_id,
            f"-{seconds} seconds"
        ))

        if cursor.rowcount > 0:
            self.conn.commit()

    def clear_events(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        DELETE FROM events
        """)

        self.conn.commit()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            name TEXT NOT NULL,
            ip TEXT,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'unknown',
            last_seen TEXT,
            offline_since TEXT,
            notification_acknowledged INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device_name TEXT NOT NULL,
            ip TEXT,
            event TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_devices_parent_id
        ON devices(parent_id)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_devices_status
        ON devices(status)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_devices_type
        ON devices(type)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_id
        ON events(id)
        """)

        self.conn.commit()

    def migrate_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info(devices)")
        columns = [row[1] for row in cursor.fetchall()]

        if "notification_acknowledged" not in columns:
            cursor.execute("""
            ALTER TABLE devices
            ADD COLUMN notification_acknowledged INTEGER DEFAULT 0
            """)

        self.conn.commit()

    def add_device(self, name, ip, device_type, parent_id=None):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO devices
        (parent_id, name, ip, type)
        VALUES (?, ?, ?, ?)
        """, (
            parent_id,
            name,
            ip,
            device_type
        ))

        self.conn.commit()
        return cursor.lastrowid

    def update_device(self, device_id, name, ip):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET name = ?,
            ip = ?
        WHERE id = ?
        """, (
            name,
            ip,
            device_id
        ))

        self.conn.commit()

    def get_devices(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            id,
            parent_id,
            name,
            ip,
            type,
            status,
            last_seen,
            offline_since,
            notification_acknowledged
        FROM devices
        """)

        return cursor.fetchall()

    def get_device_by_id(self, device_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            id,
            parent_id,
            name,
            ip,
            type,
            status,
            last_seen,
            offline_since,
            notification_acknowledged
        FROM devices
        WHERE id = ?
        """, (device_id,))

        return cursor.fetchone()

    def ip_exists(self, ip, exclude_device_id=None):
        cursor = self.conn.cursor()

        if exclude_device_id is None:
            cursor.execute("""
            SELECT id, name
            FROM devices
            WHERE ip = ?
              AND type != 'group'
            LIMIT 1
            """, (ip,))
        else:
            cursor.execute("""
            SELECT id, name
            FROM devices
            WHERE ip = ?
              AND type != 'group'
              AND id != ?
            LIMIT 1
            """, (ip, exclude_device_id))

        return cursor.fetchone()

    def update_status(self, device_id, status):
        cursor = self.conn.cursor()

        if status == "online":
            cursor.execute("""
            UPDATE devices
            SET status = ?,
                notification_acknowledged = 0
            WHERE id = ?
            """, (
                status,
                device_id
            ))
        else:
            cursor.execute("""
            UPDATE devices
            SET status = ?
            WHERE id = ?
            """, (
                status,
                device_id
            ))

        self.conn.commit()

    def update_device_name(self, device_id, new_name):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET name = ?
        WHERE id = ?
        """, (
            new_name,
            device_id
        ))

        self.conn.commit()

    def update_device_parent(self, device_id, parent_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET parent_id = ?
        WHERE id = ?
        """, (
            parent_id,
            device_id
        ))

        self.conn.commit()

    def delete_device(self, device_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        DELETE FROM devices
        WHERE id = ?
        """, (device_id,))

        self.conn.commit()

    def get_children(self, parent_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT id
        FROM devices
        WHERE parent_id = ?
        """, (parent_id,))

        return [
            row[0]
            for row in cursor.fetchall()
        ]

    def delete_branch(self, device_id):
        children = self.get_children(device_id)

        for child_id in children:
            self.delete_branch(child_id)

        cursor = self.conn.cursor()

        cursor.execute("""
        DELETE FROM devices
        WHERE id = ?
        """, (device_id,))

        self.conn.commit()

    def add_event(self, timestamp, device_name, ip, event):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO events
        (timestamp, device_name, ip, event)
        VALUES (?, ?, ?, ?)
        """, (
            timestamp,
            device_name,
            ip,
            event
        ))

        self.conn.commit()

    def get_events(self, limit=500):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            timestamp,
            device_name,
            ip,
            event
        FROM events
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    def get_unacknowledged_offline_devices(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            id,
            name,
            ip
        FROM devices
        WHERE status = 'offline'
          AND type != 'group'
          AND notification_acknowledged = 0
        """)

        return cursor.fetchall()

    def acknowledge_notification(self, device_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET notification_acknowledged = 1
        WHERE id = ?
        """, (device_id,))

        self.conn.commit()

    def acknowledge_notifications(self, device_ids):
        if not device_ids:
            return

        cursor = self.conn.cursor()

        cursor.executemany("""
        UPDATE devices
        SET notification_acknowledged = 1
        WHERE id = ?
        """, [(device_id,) for device_id in device_ids])

        self.conn.commit()

    def reset_notification_acknowledgement(self, device_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE devices
        SET notification_acknowledged = 0
        WHERE id = ?
        """, (device_id,))

        self.conn.commit()

    def set_setting(self, key, value):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO settings
        (key, value)
        VALUES (?, ?)
        """, (
            key,
            value
        ))

        self.conn.commit()

    def get_setting(self, key, default=None):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
        """, (key,))

        row = cursor.fetchone()

        if row:
            return row[0]

        return default

    def get_device_path(self, device_id):
        cursor = self.conn.cursor()

        path = []

        cursor.execute("""
        SELECT parent_id
        FROM devices
        WHERE id = ?
        """, (device_id,))

        row = cursor.fetchone()

        if not row:
            return ""

        current_id = row[0]

        while current_id:
            cursor.execute("""
            SELECT parent_id, name
            FROM devices
            WHERE id = ?
            """, (current_id,))

            row = cursor.fetchone()

            if not row:
                break

            parent_id, name = row

            path.append(name)

            current_id = parent_id

        path.reverse()

        return " → ".join(path)