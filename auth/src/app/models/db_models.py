import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app import db


def now_with_tz_info():
    return datetime.now(tz=timezone.utc)


class Role(db.Model):
    # root, admin, subscriber, user, reviewer, etc
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return self.name


user_roles = db.Table(
    "user_roles",
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id")),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String)
    registered_on = Column(DateTime(timezone=True), default=now_with_tz_info, nullable=False)
    # subscribe_expiration
    is_confirmed = Column(Boolean, default=False)
    is_root = Column(Boolean, default=False)
    roles = relationship("Role", secondary=user_roles, lazy="subquery", backref=backref("roles", lazy=True))


class UserAction(db.Model):
    __tablename__ = "user_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user_agent = Column(String)
    action_type = Column(String)  # TODO использовать enum или отдельную таблицу Actions
    action_time = Column(DateTime(timezone=True), default=now_with_tz_info)
