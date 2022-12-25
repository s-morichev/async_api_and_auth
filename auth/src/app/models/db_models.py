import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app import db


def now_with_tz_info():
    return datetime.now(tz=timezone.utc)


@enum.unique
class Permissions(enum.Enum):
    # TODO добавить разрешения при необходимости
    VIEW_FREE_FILMS = (1,)
    VIEW_PAID_FILMS = (2,)
    COMMENT = 3
    # CRUD_FILMS = 4,
    # CRUD_USERS = 5,
    # CRUD_ROLES = 6,


class Permission(db.Model):
    # все разрешения должны автоматически записываться в базу, если их там нет
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(Enum(Permissions), unique=True, nullable=False)


class Role(db.Model):
    # root, anonymous, registered, paid
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)


class RolePermissions(db.Model):
    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"))


class User(db.Model):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    registered_on = Column(DateTime(timezone=True), default=now_with_tz_info, nullable=False)
    # subscribe_expiration
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))


class Device(db.Model):
    # TODO как идентифицировать, UserAgent, fingerprint?
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    # user_agent
    usable = Column(Boolean, nullable=False)


class UserDevices(db.Model):
    __tablename__ = "user_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"))


class ActionLog(db.Model):
    __tablename__ = "action_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    action_time = Column(DateTime(timezone=True), nullable=False)
    user_device_id = Column(UUID(as_uuid=True), ForeignKey("user_devices.id"))
    action_id = Column(UUID(as_uuid=True), ForeignKey("actions.id"))


class Action(db.Model):
    __tablename__ = "actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    token = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    # user_device?
