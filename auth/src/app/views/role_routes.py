from http import HTTPStatus

from flask import Blueprint, abort, make_response, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from ..services import role_service

parser = reqparse.RequestParser()
parser.add_argument('name')


class RolesList(Resource):
    def get(self):
        return role_service.get_all_roles()

    def post(self):
        name = parser.parse_args()['name']
        # todo проверять на уже существующие роли. Сделать индекс в базе?
        if name:
            result = role_service.add_role(name)
            return result, HTTPStatus.CREATED
        return jsonify({"msg": "No role name provided"}), HTTPStatus.BAD_REQUEST


class Roles(Resource):
    def get(self, role_id):
        return role_service.get_role(role_id)

    def delete(self, role_id):
        role_service.delete_role(role_id)
        return '', HTTPStatus.NO_CONTENT

    def put(self, role_id):
        name = parser.parse_args()['name']
        role_service.update_role(role_id, name)
        return '', HTTPStatus.NO_CONTENT


class UserRoles(Resource):
    def get(self, user_id):
        return role_service.get_user_roles(user_id)

    def delete(self, user_id, role_id):
        result = role_service.delete_user_role(user_id, role_id)
        return result, HTTPStatus.OK

    def post(self, user_id, role_id):
        result = role_service.add_user_role(user_id, role_id)
        return result, HTTPStatus.CREATED
