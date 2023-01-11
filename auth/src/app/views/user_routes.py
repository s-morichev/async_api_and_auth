from http import HTTPStatus

from flask import Blueprint, abort, make_response, request
from flask_restful import reqparse, abort, Api, Resource
#from ..services import role_service

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('email')
parser.add_argument('password')

stub = {'id': 1, 'name': 'Jhon Doe'}


class Users(Resource):

    def post(self):
        """Добавить пользователя"""

        name = parser.parse_args()['name']
        email = parser.parse_args()['email']
        password = parser.parse_args()['password']
        return stub

    def patch(self, user_id):
        """Поменять данные пользователя"""

        name = parser.parse_args()['name']
        email = parser.parse_args()['email']
        password = parser.parse_args()['password']
        return stub


user_bp = Blueprint("user", __name__)
api = Api(user_bp)
api.add_resource(Users, '/users', '/users/<user_id>')




