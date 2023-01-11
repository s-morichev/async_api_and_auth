import getpass

import click
from flask import Flask

from app.db import database
from app.services import auth_service, role_service

STANDARD_ROLES = "admin", "subscriber", "user"


def init_cli(app: Flask):
    @app.cli.command("createsuperuser")
    @click.option("--email", help="Superuser email")
    @click.option("--password", help="Superuser password")
    def create_super_user(email, password):
        """Create superuser.

        Email and password can be provided via --email and --password options.
        Example: flask createsuperuser --email some_email --password some_password
        """
        if not email:
            email = input("Enter email:")
        if not password:
            password = getpass.getpass("Enter password:")
            while getpass.getpass("Confirm password:") != password:
                continue

        try:
            # TODO mark as superuser
            auth_service.register_user(email, password, email)
        except auth_service.RegisterError:
            click.echo("User with this email exists.")
            return
        click.echo("Superuser created")

    @app.cli.command("insert-roles")
    def insert_roles():
        """Add standard roles to database on application deploy."""
        for role_name in STANDARD_ROLES:
            try:
                role_service.add_role(role_name)
            except role_service.RoleError:
                pass
        click.echo("Roles inserted")

    @app.cli.command("insert-users")
    def insert_users():
        """Add users and admin for development."""
        for user_email in ("example1", "example2", "example3", "admin"):
            try:
                auth_service.register_user(user_email, "password", user_email)
            except auth_service.RegisterError:
                pass
        click.echo("Users added")
        admin = database.data.User.find_by_email("admin")
        admin_role = database.data.Role.find_by_name("admin")
        role_service.add_user_role(admin.id, admin_role.id)
        click.echo("Admin role added")
