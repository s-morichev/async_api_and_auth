from app import create_app

# need to import models somewhere so SQLAlchemy knows about this models
# from app.models.db_models import User, Role, Action, UserRole, UserAction
from app.models.db_models import Role, User, UserAction

app = create_app()



# TODO



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)