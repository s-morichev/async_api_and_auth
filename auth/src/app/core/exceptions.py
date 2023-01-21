from flask import jsonify


class AuthServiceError(Exception):
    def __init__(self, status_code, detail, *args):
        super().__init__(args)
        self.status_code = status_code
        self.detail = detail


def http_error_handler(err: AuthServiceError):
    return jsonify({"msg": err.detail}), err.status_code
