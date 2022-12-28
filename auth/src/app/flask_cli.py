from flask import Flask
from app.models.db_models import db, Role, User


def init_cli(app: Flask):
    @app.cli.command("createsuperuser")
    def create_super_user(email, password):
        pass

    @app.cli.command("insert-roles")
    def insert_roles():
        for role_name in ("admin", "subscriber", "user"):
            db.session.add(Role(name=role_name))
        db.session.commit()
        print("roles inserted")

    @app.cli.command("insert-users")
    def insert_users():
        from werkzeug.security import generate_password_hash

        default_role = db.session.query(Role).filter(Role.name == "user").first()
        for user_email in ("example1", "example2", "example3"):
            password_hash = generate_password_hash("password")
            user = User(email=user_email, password_hash=password_hash)
            user.roles.append(default_role)
            db.session.add(user)
        db.session.commit()
        print("users created")

        admin_role = db.session.query(Role).filter(Role.name == "admin").first()
        password_hash = generate_password_hash("password")
        admin_user = User(email="admin", password_hash=password_hash)
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print("admin created")
