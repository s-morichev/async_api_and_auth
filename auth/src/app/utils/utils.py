import hashlib


def device_id_from_name(device_name: str):
    return hashlib.sha256(device_name.encode("utf8")).hexdigest()
