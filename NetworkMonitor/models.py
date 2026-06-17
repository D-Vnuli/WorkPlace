class Device:
    def __init__(
            self,
            device_id,
            parent_id,
            name,
            ip,
            device_type,
            status="unknown"
    ):
        self.id = device_id
        self.parent_id = parent_id
        self.name = name
        self.ip = ip
        self.device_type = device_type
        self.status = status