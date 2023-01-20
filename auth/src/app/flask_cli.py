import getpass

import click
from flask import Flask

from app.db import database
from app.services import user_service, role_service
from app.core.exceptions import AuthServiceError
from app.core.constants import ROOT_ROLE

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
            root_user = user_service.add_user(email, password, email)
        except AuthServiceError as err:
            click.echo(err.detail)
            return
        root_role = role_service.get_role_by_name(ROOT_ROLE)
        if not root_role:
            root_role = role_service.add_role(ROOT_ROLE)
        role_service.add_user_role(root_user['id'], root_role['id'])
        click.echo("Superuser created")

    @app.cli.command("insert-roles")
    def insert_roles():
        """Add standard roles to database on application deploy."""
        for role_name in STANDARD_ROLES:
            try:
                role_service.add_role(role_name)
            except AuthServiceError:
                pass
        click.echo("Roles inserted")

    @app.cli.command("insert-users")
    def insert_users():
        """Add users and admin for development."""
        for user_email in ("example1", "example2", "example3", "admin"):
            try:
                user_service.add_user(user_email, "password", user_email)
            except AuthServiceError:
                pass
        click.echo("Users added")
        admin = database.data.User.find_by_email("admin")
        admin_role = database.data.Role.find_by_name("admin")
        role_service.add_user_role(admin.id, admin_role.id)
        click.echo("Admin role added")
