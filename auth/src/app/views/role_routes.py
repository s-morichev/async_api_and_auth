from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, abort, make_response, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from ..services import role_service
from .auth_routes import msg  # TODO move msg to common module, e.g. utils
from ..exceptions import HTTPError
from ..utils import validate_uuids

parser = reqparse.RequestParser()
parser.add_argument('name')


class RolesList(Resource):
    def get(self):
        return role_service.get_all_roles()

    def post(self):
        name = parser.parse_args()['name']
        if not name:
            raise HTTPError(status_code=HTTPStatus.BAD_REQUEST, detail="No role name provided")
        try:
            result = role_service.add_role(name)
        except role_service.RoleError as err:
            return msg(str(err)), HTTPStatus.CONFLICT
        return result, HTTPStatus.CREATED


class Roles(Resource):
    def get(self, role_id):
        validate_uuids(role_id)
        role = role_service.get_role(role_id)
        if role is None:
            return jsonify({"msg": "Not found"}), HTTPStatus.NOT_FOUND
        return role_service.get_role(role_id)

    def delete(self, role_id):
        validate_uuids(role_id)
        role_service.delete_role(role_id)
        return '', HTTPStatus.NO_CONTENT

    def put(self, role_id):
        validate_uuids(role_id)
        name = parser.parse_args()['name']
        if not name:
            raise HTTPError(status_code=HTTPStatus.BAD_REQUEST, detail="No role name provided")
        role_service.update_role(role_id, name)
        return '', HTTPStatus.NO_CONTENT


class UserRoles(Resource):
    def get(self, user_id):
        validate_uuids(user_id)
        result = role_service.get_user_roles(user_id)
        return result, HTTPStatus.OK

    def delete(self, user_id, role_id):
        validate_uuids(user_id, role_id)
        result = role_service.delete_user_role(user_id, role_id)
        return result, HTTPStatus.OK

    def post(self, user_id, role_id):
        validate_uuids(user_id, role_id)
        result = role_service.add_user_role(user_id, role_id)
        return result, HTTPStatus.CREATED


role_bp = Blueprint("role", __name__)
api = Api(role_bp)
api.add_resource(RolesList, '/roles')
api.add_resource(Roles, '/roles/<role_id>')
api.add_resource(UserRoles, '/users/<user_id>/roles', '/users/<user_id>/roles/<role_id>')
