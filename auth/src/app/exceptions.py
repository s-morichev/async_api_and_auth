from flask import jsonify

class HTTPError(Exception):
    def __init__(self, status_code, detail, *args):
        super().__init__(args)
        self.status_code = status_code
        self.detail = detail


def httperror_handler(err: HTTPError):
    return jsonify({"msg": err.detail}), err.status_code
