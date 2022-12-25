import click
from flask_migrate import Migrate

from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

# TODO
@app.cli.command("createsuperuser")
def create_super_user(email, password):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
